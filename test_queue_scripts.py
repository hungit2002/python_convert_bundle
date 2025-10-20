#!/usr/bin/env python3
"""
Script test để kiểm tra các script quản lý queue RabbitMQ
"""

import os
import sys
import subprocess
import time
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

def run_command(command):
    """Chạy command và trả về kết quả"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def test_quick_delete_info():
    """Test chức năng xem thông tin queue"""
    print("🧪 Test: Xem thông tin queue")
    print("=" * 50)
    
    command = "python quick_delete.py info"
    returncode, stdout, stderr = run_command(command)
    
    print(f"Command: {command}")
    print(f"Return code: {returncode}")
    print(f"Output: {stdout}")
    if stderr:
        print(f"Error: {stderr}")
    
    if returncode == 0:
        print("✅ Test thành công")
    else:
        print("❌ Test thất bại")
    
    print()

def test_queue_manager_info():
    """Test chức năng xem thông tin queue với queue_manager"""
    print("🧪 Test: Xem thông tin queue (queue_manager)")
    print("=" * 50)
    
    command = "python queue_manager.py --action info"
    returncode, stdout, stderr = run_command(command)
    
    print(f"Command: {command}")
    print(f"Return code: {returncode}")
    print(f"Output: {stdout}")
    if stderr:
        print(f"Error: {stderr}")
    
    if returncode == 0:
        print("✅ Test thành công")
    else:
        print("❌ Test thất bại")
    
    print()

def test_queue_manager_list():
    """Test chức năng liệt kê message"""
    print("🧪 Test: Liệt kê message")
    print("=" * 50)
    
    command = "python queue_manager.py --action list --limit 5"
    returncode, stdout, stderr = run_command(command)
    
    print(f"Command: {command}")
    print(f"Return code: {returncode}")
    print(f"Output: {stdout}")
    if stderr:
        print(f"Error: {stderr}")
    
    if returncode == 0:
        print("✅ Test thành công")
    else:
        print("❌ Test thất bại")
    
    print()

def test_help_commands():
    """Test các lệnh help"""
    print("🧪 Test: Lệnh help")
    print("=" * 50)
    
    # Test quick_delete help
    print("📋 Quick Delete Help:")
    command = "python quick_delete.py"
    returncode, stdout, stderr = run_command(command)
    print(f"Command: {command}")
    print(f"Output: {stdout}")
    print()
    
    # Test queue_manager help
    print("📋 Queue Manager Help:")
    command = "python queue_manager.py --help"
    returncode, stdout, stderr = run_command(command)
    print(f"Command: {command}")
    print(f"Output: {stdout}")
    print()

def test_invalid_commands():
    """Test các lệnh không hợp lệ"""
    print("🧪 Test: Lệnh không hợp lệ")
    print("=" * 50)
    
    # Test quick_delete với tham số không hợp lệ
    print("📋 Quick Delete - Invalid parameter:")
    command = "python quick_delete.py invalid"
    returncode, stdout, stderr = run_command(command)
    print(f"Command: {command}")
    print(f"Output: {stdout}")
    print()
    
    # Test queue_manager với action không tồn tại
    print("📋 Queue Manager - Invalid action:")
    command = "python queue_manager.py --action invalid"
    returncode, stdout, stderr = run_command(command)
    print(f"Command: {command}")
    print(f"Output: {stderr}")
    print()

def check_dependencies():
    """Kiểm tra dependencies"""
    print("🔍 Kiểm tra dependencies")
    print("=" * 50)
    
    required_packages = [
        'pika',
        'python-dotenv',
        'redis',
        'requests',
        'pandas'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: OK")
        except ImportError:
            print(f"❌ {package}: Missing")
    
    print()

def check_env_file():
    """Kiểm tra file .env"""
    print("🔍 Kiểm tra file .env")
    print("=" * 50)
    
    required_vars = [
        'RABBITMQ_HOST',
        'RABBITMQ_PORT',
        'RABBITMQ_USER',
        'RABBITMQ_PASSWORD',
        'RABBITMQ_QUEUE'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Ẩn password
            if 'PASSWORD' in var:
                print(f"✅ {var}: {'*' * len(value)}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Missing")
    
    print()

def main():
    """Hàm chính"""
    print("🚀 Bắt đầu test các script quản lý queue RabbitMQ")
    print("=" * 60)
    print()
    
    # Kiểm tra dependencies
    check_dependencies()
    
    # Kiểm tra file .env
    check_env_file()
    
    # Test các chức năng
    test_quick_delete_info()
    test_queue_manager_info()
    test_queue_manager_list()
    test_help_commands()
    test_invalid_commands()
    
    print("🎉 Hoàn thành test!")
    print()
    print("📖 Hướng dẫn sử dụng:")
    print("  - Xem thông tin queue: python quick_delete.py info")
    print("  - Xóa 1 message: python quick_delete.py 1")
    print("  - Xóa tất cả: python quick_delete.py all")
    print("  - Xem chi tiết: python queue_manager.py --action list --limit 10")

if __name__ == '__main__':
    main() 