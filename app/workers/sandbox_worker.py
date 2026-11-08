import docker
import tempfile
import os
import time

# Kết nối với Docker Desktop đang chạy trên máy Mac
client = docker.from_env()

def run_python_code(source_code: str, memory_limit: str = "256m"):
    """
    Hàm này tạo một môi trường ảo (container), lưu code của user vào đó,
    chạy thử, lấy kết quả và xóa môi trường ảo.
    """
    # 1. Tạo một thư mục tạm thời trên máy để chứa code của user
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "main.py")
        with open(file_path, "w") as f:
            f.write(source_code)
        
        try:
            start_time = time.time()
            
            # 2. Ra lệnh cho Docker tạo một cái hộp cát (Container)
            # Dùng bản python:3.12-alpine vì nó cực nhẹ (khoảng 50MB)
            logs = client.containers.run(
                image="python:3.12-alpine",
                command="python /app/main.py",
                volumes={temp_dir: {'bind': '/app', 'mode': 'ro'}}, # Đưa file code vào hộp
                working_dir="/app",
                mem_limit=memory_limit,   # Giới hạn RAM chống treo máy
                network_disabled=True,    # Ngắt mạng internet chống hack
                remove=True,              # Chạy xong tự động tiêu hủy hộp cát
                stdout=True,              # Lấy luồng kết quả bình thường
                stderr=True               # Lấy luồng báo lỗi
            )
            end_time = time.time()
            
            # Trả về kết quả thành công
            return {
                "status": "Success",
                "output": logs.decode("utf-8").strip(),
                "runtime": round(end_time - start_time, 3)
            }
            
        except docker.errors.ContainerError as e:
            # Nếu code của user bị lỗi (như lỗi cú pháp, chia cho 0...)
            return {
                "status": "Runtime Error",
                "output": e.stderr.decode("utf-8").strip(),
                "runtime": 0
            }
        except docker.errors.ImageNotFound:
            return {
                "status": "System Error",
                "output": "Chưa tải Image Python về Docker.",
                "runtime": 0
            }