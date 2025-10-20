#!/usr/bin/env python3
"""
Script xóa message nhanh chóng khỏi queue RabbitMQ
Sử dụng đơn giản: python quick_delete.py [số_lượng]
"""

import os
import pika
import json
import sys
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

def delete_messages(count=1):
    """Xóa message khỏi queue
    
    Args:
        count: Số lượng message cần xóa (mặc định là 1)
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
        
        queue_name = os.getenv('RABBITMQ_QUEUE', 'default_queue')
        
        # Lấy thông tin queue trước khi xóa
        queue = channel.queue_declare(queue=queue_name, durable=True, passive=True)
        total_messages = queue.method.message_count
        
        print(f"Queue '{queue_name}' có {total_messages} message")
        
        if total_messages == 0:
            print("Queue đã trống!")
            return
        
        # Xóa message
        deleted_count = 0
        for i in range(min(count, total_messages)):
            method_frame, header_frame, body = channel.basic_get(queue=queue_name)
            
            if method_frame is None:
                print("Không còn message nào trong queue")
                break
            
            # Xóa message
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            deleted_count += 1
            
            try:
                message = json.loads(body)
                file_name = message.get('file_name', 'Unknown')
                bundle_type = message.get('bundle_type', 'Unknown')
                print(f"✅ Đã xóa message {i+1}: {file_name} (bundle: {bundle_type})")
            except:
                print(f"✅ Đã xóa message {i+1}: Unknown")
        
        print(f"\n🎉 Đã xóa thành công {deleted_count} message")
        
        # Hiển thị thông tin còn lại
        remaining_queue = channel.queue_declare(queue=queue_name, durable=True, passive=True)
        remaining_messages = remaining_queue.method.message_count
        print(f"📊 Còn lại {remaining_messages} message trong queue")
        
        connection.close()
        
    except Exception as e:
        logger.error(f"Lỗi: {e}")
        print(f"❌ Lỗi: {e}")

def purge_all():
    """Xóa tất cả message trong queue"""
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
        
        queue_name = os.getenv('RABBITMQ_QUEUE', 'default_queue')
        
        # Lấy thông tin queue trước khi xóa
        queue = channel.queue_declare(queue=queue_name, durable=True, passive=True)
        total_messages = queue.method.message_count
        
        if total_messages == 0:
            print("Queue đã trống!")
            return
        
        print(f"⚠️  CẢNH BÁO: Sẽ xóa TẤT CẢ {total_messages} message trong queue!")
        confirm = input("Bạn có chắc chắn muốn tiếp tục? (y/N): ")
        
        if confirm.lower() != 'y':
            print("Đã hủy thao tác")
            return
        
        # Xóa tất cả message
        channel.queue_purge(queue=queue_name)
        print(f"🎉 Đã xóa thành công {total_messages} message")
        
        connection.close()
        
    except Exception as e:
        logger.error(f"Lỗi: {e}")
        print(f"❌ Lỗi: {e}")

def show_info():
    """Hiển thị thông tin queue"""
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
        
        queue_name = os.getenv('RABBITMQ_QUEUE', 'default_queue')
        
        # Lấy thông tin queue
        queue = channel.queue_declare(queue=queue_name, durable=True, passive=True)
        message_count = queue.method.message_count
        consumer_count = queue.method.consumer_count
        
        print(f"\n=== THÔNG TIN QUEUE ===")
        print(f"Queue name: {queue_name}")
        print(f"Message count: {message_count}")
        print(f"Consumer count: {consumer_count}")
        
        connection.close()
        
    except Exception as e:
        logger.error(f"Lỗi: {e}")
        print(f"❌ Lỗi: {e}")

def main():
    """Hàm chính"""
    if len(sys.argv) == 1:
        # Không có tham số, hiển thị thông tin
        show_info()
        print("\n📖 Cách sử dụng:")
        print("  python quick_delete.py [số_lượng]  - Xóa số lượng message")
        print("  python quick_delete.py all          - Xóa tất cả message")
        print("  python quick_delete.py info         - Xem thông tin queue")
        
    elif len(sys.argv) == 2:
        arg = sys.argv[1].lower()
        
        if arg == 'all':
            purge_all()
        elif arg == 'info':
            show_info()
        elif arg.isdigit():
            count = int(arg)
            delete_messages(count)
        else:
            print("❌ Tham số không hợp lệ!")
            print("Sử dụng: python quick_delete.py [số_lượng|all|info]")
    else:
        print("❌ Quá nhiều tham số!")
        print("Sử dụng: python quick_delete.py [số_lượng|all|info]")

if __name__ == '__main__':
    main() 