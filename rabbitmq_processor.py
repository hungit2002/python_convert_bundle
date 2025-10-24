import os
import time
import logging
import shutil
import pika
import json
import redis
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from file_handle import main_process, CustomException, evaluate_process_time, noti_to_tele
from convert import delete_zip_file, insert_result_to_es, move_file_to_dead_letter

max_retry = 3
# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load biến môi trường
load_dotenv()

# Khởi tạo Redis client
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT')),
    db=int(os.getenv('REDIS_DB'))
)

def download_file_from_s3(file_name, bundle_type='word'):
    """Tải file từ S3 về local
    
    Args:
        file_name: Tên file cần tải
        
    Returns:
        bool: True nếu tải thành công, False nếu thất bại
    """
    try:
        domain = os.getenv('WORD_CDN_PATH_SOURCE')
        if bundle_type == 'story':
            domain = os.getenv('STORY_CDN_PATH_SOURCE')
        if bundle_type == 'activity':
            domain = os.getenv('ACTIVITY_CDN_PATH_SOURCE')
        if bundle_type == 'courseinstall':
            domain = os.getenv('COURSEINSTALL_CDN_PATH_SOURCE')
        # Tạo URL đầy đủ
        s3_url = f"{domain}{file_name}"
        
        # Tạo đường dẫn lưu file
        save_path = os.path.join(os.getenv('WORD_ZIP_PATH_SOURCE'), file_name)
        
        # Tải file
        logger.info(f"Downloading file from S3: {s3_url}")
        response = requests.get(s3_url, stream=True)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Lưu file
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        logger.info(f"Successfully downloaded file to: {save_path}")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading file from S3: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error while downloading file: {e}")
        return False

def check_process(file_path):
    """Kiểm tra trạng thái xử lý file trong Redis"""
    file_name = os.path.basename(file_path)
    status = redis_client.get(file_name)
    if status:
        return status
    return None

def cache_process_status(file_path, status):
    """Cache trạng thái xử lý file vào Redis"""
    file_name = os.path.basename(file_path)
    redis_client.set(file_name, status)

def delete_cache(file_path):
    """Xóa cache của file trong Redis"""
    file_name = os.path.basename(file_path)
    redis_client.delete(file_name)

def remove_folder():
    """Xóa nội dung thư mục INPUT và OUTPUT"""
    step = "Clean"
    start = time.time()
    input_folder = os.getenv('INPUT')
    output_folder = os.getenv('OUTPUT')
    folders = [input_folder, output_folder]

    logger.info(step)
    for folder in folders:
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.error(f"Error cleaning folder: {e}")
    end = time.time()
    evaluate_process_time(start, end, step)

def copy_zip_file(file_path):
    """Copy file zip vào thư mục INPUT"""
    step = "Copy zip to Input"
    start = time.time()

    logger.info(step)
    if file_path:
        try:
            shutil.copy(file_path, os.getenv('INPUT'))
        except Exception as e:
            logger.error(f"Error copying file: {e}")
    end = time.time()
    evaluate_process_time(start, end, step)

def save_build_result_to_excel(file_name, bundle_type, status, ios_bundle, and_bundle, build_time, retry_count):
    """Lưu kết quả build vào file Excel
    
    Args:
        file_name: Tên file đã build
        bundle_type: Loại bundle
        status: Trạng thái build (Done/Failed)
        ios_bundle: Bundle iOS
        and_bundle: Bundle Android
        build_time: Thời gian build
        retry_count: Số lần retry
    """
    try:
        # Tạo tên file Excel với ngày tháng
        current_date = datetime.now().strftime('%Y%m%d')
        excel_file = f'./build_result/build_results_{current_date}.xlsx'
        
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs('./build_result', exist_ok=True)
        
        # Tạo dữ liệu mới
        new_data = {
            'Timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            'File Name': [file_name],
            'Bundle Type': [bundle_type],
            'Status': [status],
            'iOS Bundle': [ios_bundle],
            'Android Bundle': [and_bundle],
            'Build Time': [build_time],
            'Retry Count': [retry_count]
        }
        
        # Tạo DataFrame mới
        df_new = pd.DataFrame(new_data)
        
        # Kiểm tra file Excel đã tồn tại chưa
        if os.path.exists(excel_file):
            # Đọc file Excel hiện tại
            df_existing = pd.read_excel(excel_file)
            # Thêm dữ liệu mới vào cuối
            df_updated = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_updated = df_new
            
        # Lưu vào file Excel
        df_updated.to_excel(excel_file, index=False)
        logger.info(f"Build result saved to {excel_file}")
        
    except Exception as e:
        logger.error(f"Error saving build result to Excel: {str(e)}")

def process_message(ch, method, properties, body):
    """Xử lý message từ RabbitMQ"""
    count_retry = 1
    max_retry = 1

    try:
        message = json.loads(body)
        file_name = message.get('file_name')
        bundle_type = message.get('bundle_type', 'word')

        if not file_name:
            logger.error("Invalid message format: missing file_name")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        while count_retry <= max_retry:
            try:
                logger.info(f"Processing attempt {count_retry} of {max_retry} for file: {file_name}")

                # Download file
                if not download_file_from_s3(file_name, bundle_type):
                    raise RuntimeError(f"Failed to download file from S3: {file_name}")

                file_path = os.path.join(os.getenv('WORD_ZIP_PATH_SOURCE'), file_name)
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File not found: {file_path}")

                cache_process_status(file_path, "Processing")
                remove_folder()
                copy_zip_file(file_path)

                # Prepare folder item for processing
                upload_ios = os.getenv('WORD_IOS_S3_PATH')
                upload_android = os.getenv('WORD_AND_S3_PATH')
                upload_win32 = os.getenv('WORD_WIN32_S3_PATH')
                if bundle_type == 'story':
                    upload_ios = os.getenv('STORY_IOS_S3_PATH')
                    upload_android = os.getenv('STORY_AND_S3_PATH')
                    upload_win32 = os.getenv('STORY_WIN32_S3_PATH')
                if bundle_type == 'activity':
                    upload_ios = os.getenv('ACTIVITY_IOS_S3_PATH')
                    upload_android = os.getenv('ACTIVITY_AND_S3_PATH')
                    upload_win32 = os.getenv('ACTIVITY_WIN32_S3_PATH')
                if bundle_type == 'courseinstall':
                    upload_ios = os.getenv('COURSEINSTALL_IOS_S3_PATH')
                    upload_android = os.getenv('COURSEINSTALL_AND_S3_PATH')
                    upload_win32 = os.getenv('COURSEINSTALL_WIN32_S3_PATH')
                folder_item = {
                    'bundle_type': bundle_type,
                    'type': 'bundle',
                    'upload_ios': upload_ios,
                    'upload_android': upload_android,
                    'upload_win32': upload_win32,
                }

                result = main_process(file_path, folder_item)
                message = result[0]
                build_time = result[1]
                ios_bundle = result[2]
                and_bundle = result[3]

                if message == "Done":
                    delete_zip_file(file_path)
                    delete_cache(file_path)
                    save_build_result_to_excel(file_name, bundle_type, "Done", ios_bundle, and_bundle, build_time, count_retry)
                    logger.info(f"Successfully processed {file_name} after {count_retry} attempts")
                    break
                else:
                    delete_cache(file_path)
                    save_build_result_to_excel(file_name, bundle_type, "Failed", "Not Exist", "Not Exists", "0", count_retry)
                    if count_retry == max_retry:
                        logger.error(f"Failed to process {file_name} after {max_retry} attempts")
                        move_file_to_dead_letter(file_path, bundle_type)
                    else:
                        logger.warning(f"Retry {count_retry} failed for {file_name}, attempting again...")

            except Exception as e:
                logger.error(f"Error on attempt {count_retry}: {e}")
                if count_retry == max_retry:
                    logger.error(f"Max retries reached for {file_name}")
                    move_file_to_dead_letter(file_name, bundle_type)

            finally:
                count_retry += 1

        count_queue_messages(ch)

    except Exception as e:
        logger.error(f"Fatal error processing message: {e}")

    # ✅ Chỉ ack ở đây, sau khi xử lý xong toàn bộ retry
    ch.basic_ack(delivery_tag=method.delivery_tag)

# def process_message(ch, method, properties, body):
#     """Xử lý message từ RabbitMQ"""
#     count_retry = 1
#     max_retry = 3  # Số lần retry tối đa
#
#     try:
#         # Parse message
#         message = json.loads(body)
#         file_name = message.get('file_name')
#         bundle_type = message.get('bundle_type', 'word')
#
#         if not file_name:
#             logger.error("Invalid message format: missing file_name")
#             ch.basic_ack(delivery_tag=method.delivery_tag)
#             return
#
#         while count_retry <= max_retry:
#             logger.info(f"Processing attempt {count_retry} of {max_retry} for file: {file_name}")
#
#             # Tải file từ S3
#             if not download_file_from_s3(file_name):
#                 logger.error(f"Failed to download file from S3: {file_name}")
#                 if count_retry == max_retry:
#                     ch.basic_ack(delivery_tag=method.delivery_tag)
#                     return
#                 count_retry += 1
#                 continue
#
#             # Tạo đường dẫn file
#             file_path = os.path.join(os.getenv('WORD_ZIP_PATH_SOURCE'), file_name)
#
#             # Kiểm tra file tồn tại
#             if not os.path.exists(file_path):
#                 logger.error(f"File not found: {file_path}")
#                 if count_retry == max_retry:
#                     ch.basic_ack(delivery_tag=method.delivery_tag)
#                     return
#                 count_retry += 1
#                 continue
#
#             # Cache trạng thái xử lý
#             cache_process_status(file_path, "Processing")
#
#             # Xóa thư mục cũ
#             remove_folder()
#
#             # Copy file vào INPUT
#             copy_zip_file(file_path)
#
#             # Xử lý file
#             folder_item = {
#                 'bundle_type': bundle_type,
#                 'type': 'bundle',
#                 'upload_ios': os.getenv('WORD_IOS_S3_PATH'),
#                 'upload_android': os.getenv('WORD_AND_S3_PATH'),
#                 'upload_win32': os.getenv('WORD_WIN32_S3_PATH'),
#             }
#
#             result = main_process(file_path, folder_item)
#
#             message = result[0]
#             build_time = result[1]
#             ios_bundle = result[2]
#             and_bundle = result[3]
#
#             if message == "Done":
#                 delete_zip_file(file_path)
#                 delete_cache(file_path)
#                 # insert_result_to_es(file_path, bundle_type, message, ios_bundle, and_bundle, build_time)
#                 save_build_result_to_excel(file_name, bundle_type, "Done", ios_bundle, and_bundle, build_time, count_retry)
#                 logger.info(f"Successfully processed {file_name} after {count_retry} attempts")
#                 break
#             else:
#                 build_time = "0"
#                 ios_bundle = "Not Exist"
#                 and_bundle = "Not Exists"
#                 fail_message = "Failed"
#                 delete_cache(file_path)
#                 # insert_result_to_es(file_path, bundle_type, fail_message, ios_bundle, and_bundle, build_time)
#                 save_build_result_to_excel(file_name, bundle_type, "Failed", ios_bundle, and_bundle, build_time, count_retry)
#
#                 if count_retry == max_retry:
#                     logger.error(f"Failed to process {file_name} after {max_retry} attempts")
#                     move_file_to_dead_letter(file_path, bundle_type)
#                 else:
#                     logger.warning(f"Retry {count_retry} failed for {file_name}, attempting again...")
#                     count_retry += 1
#                     continue
#
#         # Đếm số message còn lại sau khi xử lý
#         count_queue_messages(ch)
#
#     except Exception as e:
#         logger.error(f"Error processing message: {e}")
#     finally:
#         ch.basic_ack(delivery_tag=method.delivery_tag)

def count_queue_messages(channel):
    """Đếm số lượng message còn lại trong queue
    
    Args:
        channel: Channel RabbitMQ đã được tạo
    """
    try:
        # Khai báo queue
        queue_name = os.getenv('RABBITMQ_QUEUE')
        queue = channel.queue_declare(queue=queue_name, durable=True, passive=True)
        
        # Lấy số lượng message
        message_count = queue.method.message_count
        consumer_count = queue.method.consumer_count

        message_count_file = f"Queue {queue_name} has {message_count} messages and {consumer_count} consumers"
        logger.info(message_count_file)
        noti_to_tele(message_count_file)
        return message_count

    except Exception as e:
        logger.error(f"Error counting queue messages: {e}")
        return None

def connect_to_rabbitmq():
    """Kết nối đến RabbitMQ với retry và heartbeat"""
    while True:
        try:
            # Load biến môi trường
            username = os.getenv("RABBITMQ_USER")
            password = os.getenv("RABBITMQ_PASSWORD")
            
            # Kiểm tra biến môi trường
            if not username or not password:
                logger.error("Missing RabbitMQ credentials in environment variables")
                logger.error("Please check RABBITMQ_USERNAME and RABBITMQ_PASSWORD in .env file")
                time.sleep(5)
                continue
                
            credentials = pika.PlainCredentials(username, password)
            parameters = pika.ConnectionParameters(
                host=os.getenv("RABBITMQ_HOST"),
                port=int(os.getenv("RABBITMQ_PORT")),
                credentials=credentials,
                heartbeat=600,  # Heartbeat mỗi 30 giây
                blocked_connection_timeout=600,  # Timeout sau 30 giây nếu connection bị block
                socket_timeout=10,  # Timeout cho socket operations
                connection_attempts=3,  # Số lần thử kết nối
                retry_delay=5  # Delay 5 giây giữa các lần retry
            )
            
            logger.info(f"Connecting to RabbitMQ at {os.getenv('RABBITMQ_HOST')}:{os.getenv('RABBITMQ_PORT')}")
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.basic_qos(prefetch_count=1)
            logger.info("Successfully connected to RabbitMQ")
            return connection, channel
            
        except (pika.exceptions.AMQPConnectionError, 
                pika.exceptions.AMQPChannelError,
                pika.exceptions.StreamLostError) as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            logger.info("Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            logger.info("Retrying in 5 seconds...")
            time.sleep(5)

def main():
    """Hàm chính để xử lý message từ RabbitMQ"""
    while True:
        try:
            # Kết nối đến RabbitMQ
            connection, channel = connect_to_rabbitmq()
            
            # Khai báo queue
            channel.queue_declare(queue=os.getenv('RABBITMQ_QUEUE'), durable=True)
            count_queue_messages(channel)
            
            # Bắt đầu consume messages
            channel.basic_consume(
                queue=os.getenv('RABBITMQ_QUEUE'),
                on_message_callback=process_message
            )
            
            logger.info('Started consuming messages...')
            channel.start_consuming()
            
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Lost connection to RabbitMQ: {str(e)}")
            logger.info("Attempting to reconnect...")
            time.sleep(5)
        except pika.exceptions.AMQPChannelError as e:
            logger.error(f"Channel error: {str(e)}")
            logger.info("Attempting to reconnect...")
            time.sleep(5)
        except pika.exceptions.StreamLostError as e:
            logger.error(f"Stream lost: {str(e)}")
            logger.info("Attempting to reconnect...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Unexpected error in main: {str(e)}")
            logger.info("Attempting to reconnect...")
            time.sleep(5)
        finally:
            # Đóng kết nối nếu còn mở
            if 'connection' in locals() and connection.is_open:
                try:
                    connection.close()
                except:
                    pass

if __name__ == '__main__':
    main() 