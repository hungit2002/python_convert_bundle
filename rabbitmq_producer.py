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
        # "1864_1_4307_1689046813.zip",
        # "2237_1_4307_1688700522.zip",
        # "2314_1_4307_1688701117.zip",
        # "193_1_4307_1688695954.zip",
        # "4015_1_4307_1688701242.zip",
        # "183_1_4451_1692680631.zip",
        # "789_1_4274_1684139406.zip",
        # "66_1_4274_1684140481.zip",
        # "2313_1_4307_1688701110.zip",
        # "437_1_4307_1688696385.zip",
        # "84_1_4307_1688695719.zip",
        # "209_1_4307_1688696012.zip",
        # "121_1_4451_1692680594.zip",
        # "578_1_4451_1692680981.zip",
        # "417_1_4451_1692680920.zip",
        # "1342_1_4307_1688697749.zip",
        # "1548598-1755172046-efx.zip",
        # "57_1_101262_1754970273.zip",
        # "82_1_101262_1754970284.zip",
        # "99_1_101262_1754970290.zip",
        # "149_1_101261_1754962290.zip",
        # "303_1_101261_1754962302.zip",
        # "415_1_101261_1754962310.zip",
        # "577_1_101261_1754962312.zip",
        # "2305_1_4307_1755229801.zip",
        # "1548598-1755230180-nsx.zip",
        # "eb903ed9-c48b-42f0-8392-02a0f80b3908_380255.zip",
        # "2322_1_4532_1706335409.zip",
        # "2317_1_4307_1688701148.zip",
        # "2305_1_4307_1688701057.zip",
        # "57_1_101262_1754970273.zip",
        # "58_1_101262_1754970275.zip",
        # "82_1_101262_1754970284.zip",
        # "87_1_101262_1754970284.zip",
        # "99_1_101262_1754970290.zip",
        # "149_1_101261_1754962290.zip",
        # "930_1_101262_1754970339.zip",
        # "944_1_101262_1754970351.zip",
        # "954_1_101262_1754970356.zip",
        # "1209_1_101262_1754970394.zip",
        # "1824_1_4307_1689046737.zip",
        # "4020_1_4307_1688701289.zip",
        # "1829_1_4307_1689046746.zip",
        # "250_1_4307_1688696072.zip",
        # "1552071-1756188876-geh.zip"
        # "course_install_ms2.0_262_1756382672.zip"
        # "course_install_ms2.0_264_1756430973.zip",
        # "course_install_ms2.0_266_1756452508.zip",
        # "course_install_ms2.0_268_1756882568.zip",
        # "1552078-1756995732-mfi.zip",
        # "1552085-1756996766-pqm.zip",
        # "1552091-1756999082-snx.zip",
        # "course_install_ms2.0_270_1757001134.zip",
        # "1552078-1757042986-ckk.zip",
        # "course_install_ms2.0_271_1757043279.zip",
        # "1552107-1757066151-dza.zip",
        # "1552078-1757042986-ckk-2.zip",
        # "1552085-1756996766-pqm-2.zip",
        # "1552091-1757000882-nsr-2.zip",
        # "1552107-1757068349-sps-2.zip",
        # "1552118-1757074522-mgr-2.zip",
        # "1552121-1757083405-frr-2.zip",
        # "1552127-1757084248-kqf-2.zip",
        # "1552135-1757085442-jof-2.zip",
        # "1552136-1757086492-ehq-2.zip",
        # "1552137-1757086909-rli-2.zip",
        # "1552147-1757171287-uqp-2.zip",
        # "1552148-1757171023-tli-2.zip",
        # "1552149-1757170748-gsc-2.zip",
        # "1552150-1757170343-qzv-2.zip",
        # "1552151-1757169908-fyv-2.zip",
        # "1552228-1757223651-rkh-2.zip",
        # "1552229-1757223918-ueb-2.zip",
        # "1552230-1757224116-fqb-2.zip",
        # "1552231-1757224412-drv-2.zip",
        # "1552232-1757224617-kga-2.zip",
        # "1552233-1757224829-akg-2.zip",
        # "1552234-1757225140-gqk-2.zip",
        # "1552235-1757225376-dle-2.zip",
        # "1552237-1757226227-gcj-2.zip",
        # "1552238-1757226425-jrw-2.zip",
        # "1552107-1757475921-pqq-3.zip",
        # "1552121-1757486291-bsz-3.zip",
        # "1552127-1757475664-bbs-3.zip",
        # "1552147-1757476292-mqg-3.zip",
        # "1552232-1757476434-mdp-3.zip",
        # "1552233-1757476469-fhx-3.zip",
        # "1552235-1757477823-uol-3.zip",
        # "4047_1_101269_1757488551.zip",
        # "4107_1_101271_1757493403.zip",
        # "4049_1_101270_1757492109.zip",
        # "2259_1_101266_1757478050.zip",
        # "2246_1_101265_1757477494.zip",
        # "4106_1_101271_1757493403.zip",
        # "1180_1_101271_1757493106.zip",
        # "2241_1_101265_1757477540.zip",
        # "1552091-1757500492-vfm-3.zip",
        # "1552135-1757494797-vhu-3.zip",
        # "1552137-1757553484-znv-3.zip",
        # "1552148-1757514950-ogs-3.zip",
        # "1552149-1757498945-sqd-3.zip",
        # "1552151-1757500605-xij-3.zip",
        # "1552228-1757499117-wdj-3.zip",
        # "1552229-1757552888-lso-3.zip",
        # "1552230-1757499436-iur-3.zip",
        # "1552234-1757500534-rmo-3.zip",
        # "1552238-1757499638-wgu-3.zip",
        # "1552230-1757499436-iur-4.zip",
        # "1552078-1757563375-klm-3.zip",
        # "course_install_ms2.0_321_1759130114.zip"
        # "935_1_4451_1692681171.zip",
        # "939_1_4451_1692681219.zip",
        # "258_1_4451_1692689815.zip",
        # "482_1_4273_1683568823.zip",
        # "542_1_4313_1690251715.zip",
        # "1251_1_4273_1680450190.zip",
        # "1259_1_4273_1680450271.zip",
        # "1255_1_4274_1684134549.zip",
        # "1246_1_4273_1683622409.zip",
        # "513_1_4274_1684139874.zip",
        # "1256_1_4274_1684138251.zip",
        # "1261_1_4274_1684134529.zip",
        # "120_1_4435_1691084084.zip",
        # "1210_1_4456_1694505862.zip",
        # "1218_1_4451_1692690022.zip",
        # "405_1_4273_1683538960.zip",
        # "1260_1_4273_1683694861.zip",
        # "64_1_4451_1692689718.zip",
        # "1257_1_4274_1684134538.zip",
        # "1144_1_4273_1680446858.zip",
        # "1265_1_4273_1680450336.zip",
        # "224_1_4435_1691084113.zip",
        # "224_1_4435_1691084113.zip",
        # "course_install_ms2.0_324_1759418441.zip"
        "course_install_ms2.0_354_1761281088.zip"
    ]

    if zip_files:
        # Gửi nhiều file vào queue
        # send_multiple_files(zip_files,"activity")
        # send_multiple_files(zip_files,"word")
        send_multiple_files(zip_files,"courseinstall")
    else:
        logger.error("No zip files found in folder") 