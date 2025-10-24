#!/usr/bin/env python3
"""
Script quản lý queue RabbitMQ
Chức năng: Xóa message, xem thông tin queue, quản lý consumer
"""

import os
import pika
import json
import logging
import argparse
from typing import Optional, List, Dict, Any
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

class RabbitMQQueueManager:
    """Class quản lý queue RabbitMQ"""
    
    def __init__(self, queue_name: Optional[str] = None):
        """Khởi tạo kết nối RabbitMQ
        
        Args:
            queue_name: Tên queue chỉ định; nếu không truyền sẽ dùng từ ENV
        """
        self.connection = None
        self.channel = None
        self.queue_name = queue_name or os.getenv('RABBITMQ_QUEUE', 'default_queue')
        self.connect()
    
    def connect(self):
        """Kết nối đến RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(
                os.getenv('RABBITMQ_USER'),
                os.getenv('RABBITMQ_PASSWORD')
            )
            parameters = pika.ConnectionParameters(
                host=os.getenv('RABBITMQ_HOST'),
                port=int(os.getenv('RABBITMQ_PORT')),
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=600,
                socket_timeout=10
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info(f"Đã kết nối thành công đến RabbitMQ tại {os.getenv('RABBITMQ_HOST')}:{os.getenv('RABBITMQ_PORT')}")
            
        except Exception as e:
            logger.error(f"Lỗi kết nối RabbitMQ: {e}")
            raise
    
    def get_queue_info(self) -> Dict[str, Any]:
        """Lấy thông tin queue
        
        Returns:
            Dict chứa thông tin queue (message_count, consumer_count, queue_name)
        """
        try:
            queue = self.channel.queue_declare(
                queue=self.queue_name, 
                durable=True, 
                passive=True
            )
            
            info = {
                'queue_name': self.queue_name,
                'message_count': queue.method.message_count,
                'consumer_count': queue.method.consumer_count
            }
            
            logger.info(f"Queue '{self.queue_name}': {info['message_count']} messages, {info['consumer_count']} consumers")
            return info
            
        except Exception as e:
            logger.error(f"Lỗi lấy thông tin queue: {e}")
            return {}
    
    def purge_queue(self) -> bool:
        """Xóa tất cả message trong queue
        
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            # Lấy thông tin queue trước khi xóa
            queue_info = self.get_queue_info()
            message_count = queue_info.get('message_count', 0)
            
            if message_count == 0:
                logger.info("Queue đã trống, không có message nào để xóa")
                return True
            
            # Xóa tất cả message
            self.channel.queue_purge(queue=self.queue_name)
            logger.info(f"Đã xóa thành công {message_count} message khỏi queue '{self.queue_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi xóa queue: {e}")
            return False
    
    def delete_messages_by_condition(self, file_name: Optional[str] = None, 
                                   bundle_type: Optional[str] = None,
                                   max_messages: int = 100) -> int:
        """Xóa message theo điều kiện
        
        Args:
            file_name: Tên file cần xóa (optional)
            bundle_type: Loại bundle cần xóa (optional)
            max_messages: Số lượng message tối đa để xóa
            
        Returns:
            int: Số lượng message đã xóa
        """
        try:
            deleted_count = 0
            processed_count = 0
            
            while processed_count < max_messages:
                # Lấy message từ queue
                method_frame, header_frame, body = self.channel.basic_get(queue=self.queue_name)
                
                if method_frame is None:
                    logger.info("Không còn message nào trong queue")
                    break
                
                try:
                    # Parse message
                    message = json.loads(body)
                    msg_file_name = message.get('file_name')
                    msg_bundle_type = message.get('bundle_type')
                    
                    # Kiểm tra điều kiện
                    should_delete = True
                    
                    if file_name and msg_file_name != file_name:
                        should_delete = False
                    
                    if bundle_type and msg_bundle_type != bundle_type:
                        should_delete = False
                    
                    if should_delete:
                        # Xóa message bằng cách ack
                        self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                        deleted_count += 1
                        logger.info(f"Đã xóa message: {msg_file_name} (bundle_type: {msg_bundle_type})")
                    else:
                        # Reject message để đưa về queue
                        self.channel.basic_reject(delivery_tag=method_frame.delivery_tag, requeue=True)
                    
                    processed_count += 1
                    
                except json.JSONDecodeError:
                    # Nếu message không phải JSON, xóa luôn
                    self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                    deleted_count += 1
                    logger.warning("Đã xóa message không hợp lệ (không phải JSON)")
                    processed_count += 1
                
                except Exception as e:
                    # Nếu có lỗi, reject message
                    self.channel.basic_reject(delivery_tag=method_frame.delivery_tag, requeue=True)
                    logger.error(f"Lỗi xử lý message: {e}")
                    processed_count += 1
            
            logger.info(f"Đã xử lý {processed_count} message, xóa {deleted_count} message")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Lỗi xóa message theo điều kiện: {e}")
            return 0
    
    def delete_messages_by_count(self, count: int) -> int:
        """Xóa message theo số lượng
        
        Args:
            count: Số lượng message cần xóa
            
        Returns:
            int: Số lượng message đã xóa thực tế
        """
        try:
            deleted_count = 0
            
            for i in range(count):
                # Lấy message từ queue
                method_frame, header_frame, body = self.channel.basic_get(queue=self.queue_name)
                
                if method_frame is None:
                    logger.info("Không còn message nào trong queue")
                    break
                
                # Xóa message
                self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                deleted_count += 1
                
                try:
                    message = json.loads(body)
                    file_name = message.get('file_name', 'Unknown')
                    logger.info(f"Đã xóa message {i+1}: {file_name}")
                except:
                    logger.info(f"Đã xóa message {i+1}: Unknown")
            
            logger.info(f"Đã xóa thành công {deleted_count} message")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Lỗi xóa message theo số lượng: {e}")
            return 0
    
    def list_messages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Liệt kê các message trong queue (chỉ xem, không xóa)
        
        Args:
            limit: Số lượng message tối đa để xem
            
        Returns:
            List: Danh sách message
        """
        try:
            messages = []
            processed_count = 0
            
            # Lấy thông tin queue trước
            queue_info = self.get_queue_info()
            actual_message_count = queue_info.get('message_count', 0)
            
            if actual_message_count == 0:
                logger.info("Queue trống, không có message nào")
                return []
            
            # Giới hạn số message thực tế có trong queue
            max_to_process = min(limit, actual_message_count)
            
            while processed_count < max_to_process:
                # Lấy message từ queue
                method_frame, header_frame, body = self.channel.basic_get(queue=self.queue_name)
                
                if method_frame is None:
                    break
                
                try:
                    message = json.loads(body)
                    messages.append({
                        'index': processed_count + 1,
                        'file_name': message.get('file_name'),
                        'bundle_type': message.get('bundle_type'),
                        'raw_message': message
                    })
                except json.JSONDecodeError:
                    messages.append({
                        'index': processed_count + 1,
                        'file_name': 'Invalid JSON',
                        'bundle_type': 'Unknown',
                        'raw_message': body.decode('utf-8', errors='ignore')
                    })
                
                # Reject để đưa message về queue
                self.channel.basic_reject(delivery_tag=method_frame.delivery_tag, requeue=True)
                processed_count += 1
            
            logger.info(f"Đã xem {processed_count} message từ {actual_message_count} message có trong queue")
            return messages
            
        except Exception as e:
            logger.error(f"Lỗi liệt kê message: {e}")
            return []
    
    def close(self):
        """Đóng kết nối"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Đã đóng kết nối RabbitMQ")

def main():
    """Hàm chính"""
    parser = argparse.ArgumentParser(description='Quản lý queue RabbitMQ')
    parser.add_argument('--action', '-a', required=True, 
                       choices=['info', 'purge', 'delete-by-condition', 'delete-by-count', 'list'],
                       help='Hành động cần thực hiện')
    parser.add_argument('--queue', '-q', 
                       help='Tên queue chỉ định (ghi đè ENV RABBITMQ_QUEUE)')
    parser.add_argument('--file-name', '-f', 
                       help='Tên file để lọc (cho delete-by-condition)')
    parser.add_argument('--bundle-type', '-b', 
                       help='Loại bundle để lọc (cho delete-by-condition)')
    parser.add_argument('--count', '-c', type=int, default=1,
                       help='Số lượng message cần xóa (cho delete-by-count)')
    parser.add_argument('--limit', '-l', type=int, default=10,
                       help='Số lượng message tối đa để xem (cho list)')
    parser.add_argument('--max-messages', '-m', type=int, default=100,
                       help='Số lượng message tối đa để xử lý (cho delete-by-condition)')
    parser.add_argument('--confirm', action='store_true',
                       help='Xác nhận thực hiện hành động')
    
    args = parser.parse_args()
    
    try:
        # Khởi tạo queue manager
        manager = RabbitMQQueueManager(queue_name=args.queue)
        
        if args.action == 'info':
            # Hiển thị thông tin queue
            info = manager.get_queue_info()
            print(f"\n=== THÔNG TIN QUEUE ===")
            print(f"Queue name: {info.get('queue_name')}")
            print(f"Message count: {info.get('message_count')}")
            print(f"Consumer count: {info.get('consumer_count')}")
            
        elif args.action == 'purge':
            # Xóa tất cả message
            if not args.confirm:
                print("⚠️  CẢNH BÁO: Hành động này sẽ xóa TẤT CẢ message trong queue!")
                confirm = input("Bạn có chắc chắn muốn tiếp tục? (y/N): ")
                if confirm.lower() != 'y':
                    print("Đã hủy thao tác")
                    return
            
            success = manager.purge_queue()
            if success:
                print("✅ Đã xóa tất cả message thành công")
            else:
                print("❌ Lỗi khi xóa message")
                
        elif args.action == 'delete-by-condition':
            # Xóa message theo điều kiện
            if not args.file_name and not args.bundle_type:
                print("❌ Cần chỉ định ít nhất một điều kiện (file-name hoặc bundle-type)")
                return
            
            if not args.confirm:
                conditions = []
                if args.file_name:
                    conditions.append(f"file_name = '{args.file_name}'")
                if args.bundle_type:
                    conditions.append(f"bundle_type = '{args.bundle_type}'")
                
                print(f"⚠️  CẢNH BÁO: Sẽ xóa message với điều kiện: {' AND '.join(conditions)}")
                confirm = input("Bạn có chắc chắn muốn tiếp tục? (y/N): ")
                if confirm.lower() != 'y':
                    print("Đã hủy thao tác")
                    return
            
            deleted_count = manager.delete_messages_by_condition(
                file_name=args.file_name,
                bundle_type=args.bundle_type,
                max_messages=args.max_messages
            )
            print(f"✅ Đã xóa {deleted_count} message")
            
        elif args.action == 'delete-by-count':
            # Xóa message theo số lượng
            if not args.confirm:
                print(f"⚠️  CẢNH BÁO: Sẽ xóa {args.count} message đầu tiên trong queue!")
                confirm = input("Bạn có chắc chắn muốn tiếp tục? (y/N): ")
                if confirm.lower() != 'y':
                    print("Đã hủy thao tác")
                    return
            
            deleted_count = manager.delete_messages_by_count(args.count)
            print(f"✅ Đã xóa {deleted_count} message")
            
        elif args.action == 'list':
            # Liệt kê message
            messages = manager.list_messages(args.limit)
            if not messages:
                print("Queue trống hoặc không có message nào")
            else:
                print(f"\n=== DANH SÁCH {len(messages)} MESSAGE ĐẦU TIÊN ===")
                for msg in messages:
                    print(f"{msg['index']}. File: {msg['file_name']}, Bundle: {msg['bundle_type']}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Đã hủy thao tác bởi người dùng")
    except Exception as e:
        logger.error(f"Lỗi: {e}")
        print(f"❌ Lỗi: {e}")
    finally:
        if 'manager' in locals():
            manager.close()

if __name__ == '__main__':
    main() 