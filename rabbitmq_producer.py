import os
import pika
import json
import logging
from dotenv import load_dotenv

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load biến môi trường
load_dotenv()

def get_zip_files(folder_path):
    """Lấy danh sách tất cả file zip trong thư mục
    
    Args:
        folder_path: Đường dẫn thư mục cần đọc
        
    Returns:
        list: Danh sách tên các file zip
    """
    try:
        # Kiểm tra thư mục tồn tại
        if not os.path.exists(folder_path):
            logger.error(f"Folder not found: {folder_path}")
            return []
            
        # Lấy danh sách file
        zip_files = []
        for file_name in os.listdir(folder_path):
            # Kiểm tra file có phải là zip không
            if file_name.lower().endswith('.zip'):
                zip_files.append(file_name)
                
        logger.info(f"Found {len(zip_files)} zip files in {folder_path}")
        return zip_files
        
    except Exception as e:
        logger.error(f"Error reading zip files from folder: {str(e)}")
        return []

def send_message(file_name, bundle_type='word'):
    """Gửi message vào RabbitMQ queue"""
    try:
        # Kết nối RabbitMQ
        credentials = pika.PlainCredentials(
            os.getenv('RABBITMQ_USER'),
            os.getenv('RABBITMQ_PASSWORD')
        )
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=os.getenv('RABBITMQ_HOST'),
                port=int(os.getenv('RABBITMQ_PORT')),
                credentials=credentials
            )
        )
        channel = connection.channel()

        # Khai báo queue
        queue_name = os.getenv('RABBITMQ_QUEUE')
        channel.queue_declare(queue=queue_name, durable=True)

        # Tạo message
        message = {
            'file_name': file_name,
            'bundle_type': bundle_type
        }

        # Gửi message
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )

        logger.info(f"Sent message for file: {file_name}")
        connection.close()

    except Exception as e:
        logger.error(f"Error sending message: {e}")

def send_multiple_files(file_list, bundle_type='word'):
    """Gửi nhiều file vào RabbitMQ queue
    
    Args:
        file_list: Danh sách tên file cần gửi
        bundle_type: Loại bundle (mặc định là 'word')
    """
    try:
        # Kết nối RabbitMQ
        credentials = pika.PlainCredentials(
            os.getenv('RABBITMQ_USER'),
            os.getenv('RABBITMQ_PASSWORD')
        )
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=os.getenv('RABBITMQ_HOST'),
                port=int(os.getenv('RABBITMQ_PORT')),
                credentials=credentials
            )
        )
        channel = connection.channel()

        # Khai báo queue
        queue_name = os.getenv('RABBITMQ_QUEUE')
        channel.queue_declare(queue=queue_name, durable=True)

        # Gửi từng file
        for file_name in file_list:
            message = {
                'file_name': file_name,
                'bundle_type': bundle_type
            }

            channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                )
            )
            logger.info(f"Sent message for file: {file_name}")

        connection.close()
        logger.info(f"Successfully sent {len(file_list)} files to queue")

    except Exception as e:
        logger.error(f"Error sending multiple files: {e}")

if __name__ == '__main__':
    # Lấy danh sách file zip từ thư mục
    zip_folder = os.getenv('WORD_FILE_NAME_SOURCE')
    # zip_files = get_zip_files(zip_folder)
    zip_files = [
       "21487ce0-f54e-47be-8fd1-50a5d3a72aee_379900.zip"
    ]

    if zip_files:
        # Gửi nhiều file vào queue
        send_multiple_files(zip_files)
    else:
        logger.error("No zip files found in folder") 