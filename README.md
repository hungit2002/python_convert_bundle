# Hệ thống xử lý Word Bundle với RabbitMQ và Redis

## Mô tả
Hệ thống xử lý Word Bundle tự động sử dụng RabbitMQ để quản lý hàng đợi và Redis để theo dõi trạng thái xử lý. Hệ thống hỗ trợ xử lý song song nhiều file Word Bundle với khả năng mở rộng cao.

## Cài đặt

### Yêu cầu hệ thống
- Python 3.8+
- RabbitMQ Server
- Redis Server
- Unity (để xử lý bundle)

### Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### Cấu hình môi trường
Tạo file `.env` từ `.env.example` và cập nhật các thông số:
```env
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_QUEUE=word_bundle_queue

# Folder
INPUT=./input
OUTPUT=./output
WORD_ZIP_PATH_SOURCE=./word_zip_source
TEST_OUTPUT=./test_output

# Unity
UNITY_PATH=/Applications/Unity/Hub/Editor/2022.3.18f1/Unity.app/Contents/MacOS/Unity
UNITY_PROJECT_PATH=/path/to/unity/project

# Telegram
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## Luồng xử lý

### 1. Producer (rabbitmq_producer.py)
- Nhận danh sách các file Word Bundle cần xử lý
- Gửi message vào RabbitMQ queue với thông tin:
  ```json
  {
    "file_name": "ten_file.zip",
    "bundle_type": "word"
  }
  ```

### 2. Consumer (rabbitmq_processor.py)
1. **Nhận message từ queue**
   - Parse message để lấy `file_name` và `bundle_type`

2. **Tải file từ S3**
   - Tạo URL đầy đủ: `https://vnmedia2.monkeyuni.net/App/zip/hdr/word/{file_name}`
   - Tải file về thư mục `WORD_ZIP_PATH_SOURCE`
   - Xử lý các lỗi tải file

3. **Kiểm tra và xử lý file**
   - Kiểm tra file tồn tại trong thư mục `WORD_ZIP_PATH_SOURCE`
   - Cache trạng thái "Processing" vào Redis
   - Xóa nội dung thư mục INPUT và OUTPUT
   - Copy file vào thư mục INPUT

4. **Xử lý Bundle**
   - Gọi hàm `main_process` từ `file_handle.py`
   - Xử lý file với Unity
   - Kiểm tra kết quả xử lý

5. **Cập nhật trạng thái**
   - Xóa cache trong Redis sau khi xử lý xong
   - Đếm số message còn lại trong queue
   - Gửi thông báo qua Telegram

6. **Xác nhận message**
   - Gửi ACK cho RabbitMQ sau khi xử lý xong

### 3. Xử lý song song
- Mỗi consumer chạy trong một process riêng biệt
- Có thể chạy nhiều consumer trên cùng một máy
- Số lượng consumer tối ưu = số CPU cores - 1

## Sử dụng

### Chạy Producer
```bash
python rabbitmq_producer.py
```

### Chạy Consumer
```bash
python rabbitmq_processor.py
```

### Gửi nhiều file
```python
test_files = [
    "file1.zip",
    "file2.zip",
    "file3.zip"
]
send_multiple_files(test_files)
```

## Monitoring
- Log được lưu với format: `%(asctime)s - %(levelname)s - %(message)s`
- Thông báo qua Telegram khi:
  - Bắt đầu xử lý file
  - Xử lý thành công/thất bại
  - Số message còn lại trong queue

## Xử lý lỗi
- Tự động retry khi tải file từ S3 thất bại
- Xóa cache khi xử lý thất bại
- Gửi thông báo lỗi qua Telegram
- Log đầy đủ thông tin lỗi

## Bảo mật
- Sử dụng biến môi trường cho thông tin nhạy cảm
- Xác thực RabbitMQ với username/password
- Kiểm tra tính hợp lệ của file trước khi xử lý

## Cấu trúc thư mục

```
.
├── rabbitmq_processor.py  # Consumer xử lý message từ RabbitMQ
├── rabbitmq_producer.py   # Producer gửi message vào RabbitMQ
├── file_handle.py        # Xử lý file word và build bundle
├── convert.py            # Luồng xử lý cũ (không sử dụng)
├── write_result.py       # Ghi kết quả xử lý
└── requirements.txt      # Danh sách thư viện cần thiết
``` 