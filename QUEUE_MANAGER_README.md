# 🐰 Quản Lý Queue RabbitMQ

Bộ script để quản lý và xóa message khỏi queue RabbitMQ một cách an toàn và hiệu quả.

## 📁 Các File Script

### 1. `queue_manager.py` - Script quản lý queue đầy đủ tính năng

Script này cung cấp các chức năng quản lý queue chi tiết với nhiều tùy chọn.

#### Cách sử dụng:

```bash
# Xem thông tin queue
python queue_manager.py --action info

# Xóa tất cả message trong queue
python queue_manager.py --action purge --confirm

# Xóa message theo điều kiện
python queue_manager.py --action delete-by-condition --file-name "example.zip" --confirm
python queue_manager.py --action delete-by-condition --bundle-type "story" --confirm

# Xóa message theo số lượng
python queue_manager.py --action delete-by-count --count 5 --confirm

# Liệt kê message (chỉ xem, không xóa)
python queue_manager.py --action list --limit 20
```

#### Các tùy chọn:

- `--action, -a`: Hành động cần thực hiện
  - `info`: Xem thông tin queue
  - `purge`: Xóa tất cả message
  - `delete-by-condition`: Xóa message theo điều kiện
  - `delete-by-count`: Xóa message theo số lượng
  - `list`: Liệt kê message (chỉ xem)

- `--file-name, -f`: Tên file để lọc (cho delete-by-condition)
- `--bundle-type, -b`: Loại bundle để lọc (cho delete-by-condition)
- `--count, -c`: Số lượng message cần xóa (cho delete-by-count)
- `--limit, -l`: Số lượng message tối đa để xem (cho list)
- `--max-messages, -m`: Số lượng message tối đa để xử lý (cho delete-by-condition)
- `--confirm`: Xác nhận thực hiện hành động (bỏ qua confirm dialog)

### 2. `quick_delete.py` - Script xóa message nhanh chóng

Script đơn giản để xóa message nhanh chóng với cú pháp dễ nhớ.

#### Cách sử dụng:

```bash
# Xem thông tin queue
python quick_delete.py

# Xem thông tin queue
python quick_delete.py info

# Xóa 1 message
python quick_delete.py 1

# Xóa 5 message
python quick_delete.py 5

# Xóa tất cả message
python quick_delete.py all
```

## ⚠️ Lưu Ý Quan Trọng

### 🔒 Bảo Mật
- **Luôn kiểm tra kỹ** trước khi xóa message
- Sử dụng `--confirm` để bỏ qua confirm dialog (chỉ khi chắc chắn)
- Backup dữ liệu quan trọng trước khi thực hiện thao tác xóa

### 🎯 Các Loại Xóa Message

1. **Xóa tất cả (Purge)**: Xóa toàn bộ message trong queue
   - ⚠️ **Nguy hiểm**: Mất tất cả dữ liệu
   - ✅ **An toàn**: Có confirm dialog

2. **Xóa theo điều kiện**: Xóa message theo file_name hoặc bundle_type
   - ✅ **An toàn**: Chỉ xóa message thỏa mãn điều kiện
   - 🔍 **Linh hoạt**: Có thể kết hợp nhiều điều kiện

3. **Xóa theo số lượng**: Xóa N message đầu tiên trong queue
   - ⚠️ **Cẩn thận**: Xóa theo thứ tự FIFO
   - 📊 **Kiểm soát**: Biết chính xác số lượng xóa

4. **Liệt kê (List)**: Chỉ xem message, không xóa
   - ✅ **An toàn tuyệt đối**: Không thay đổi queue
   - 🔍 **Kiểm tra**: Xem nội dung message trước khi quyết định

## 🛠️ Cài Đặt Và Cấu Hình

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Cấu hình biến môi trường
Tạo file `.env` với các thông tin sau:

```env
# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=your_username
RABBITMQ_PASSWORD=your_password
RABBITMQ_QUEUE=your_queue_name

# Redis Configuration (nếu cần)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### 3. Kiểm tra kết nối
```bash
# Kiểm tra thông tin queue
python quick_delete.py info
```

## 📋 Ví Dụ Sử Dụng Thực Tế

### Tình huống 1: Xóa message lỗi
```bash
# Xem message trong queue
python queue_manager.py --action list --limit 10

# Xóa message có file_name cụ thể bị lỗi
python queue_manager.py --action delete-by-condition --file-name "error_file.zip" --confirm
```

### Tình huống 2: Xóa message cũ
```bash
# Xóa tất cả message của bundle_type "story"
python queue_manager.py --action delete-by-condition --bundle-type "story" --confirm
```

### Tình huống 3: Dọn dẹp queue
```bash
# Xóa 10 message đầu tiên
python quick_delete.py 10

# Hoặc xóa tất cả nếu cần
python quick_delete.py all
```

### Tình huống 4: Kiểm tra trạng thái
```bash
# Xem thông tin queue
python quick_delete.py info

# Xem chi tiết message
python queue_manager.py --action list --limit 20
```

## 🔧 Troubleshooting

### Lỗi kết nối RabbitMQ
```
❌ Lỗi: AMQPConnectionError
```
**Giải pháp:**
- Kiểm tra RabbitMQ server có đang chạy không
- Kiểm tra thông tin kết nối trong file `.env`
- Kiểm tra firewall/network

### Lỗi xác thực
```
❌ Lỗi: AMQPChannelError: (403) ACCESS_REFUSED
```
**Giải pháp:**
- Kiểm tra username/password trong file `.env`
- Kiểm tra quyền truy cập queue

### Queue không tồn tại
```
❌ Lỗi: Queue not found
```
**Giải pháp:**
- Kiểm tra tên queue trong file `.env`
- Tạo queue nếu chưa tồn tại

## 📊 Monitoring

### Theo dõi số lượng message
```bash
# Tạo script monitor
while true; do
    python quick_delete.py info
    sleep 30
done
```

### Log monitoring
Tất cả script đều có logging chi tiết, có thể theo dõi qua:
- Console output
- Log files (nếu cấu hình)

## 🤝 Đóng Góp

Nếu bạn muốn cải thiện script, vui lòng:
1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## 📄 License

Script này được phát hành dưới MIT License. 