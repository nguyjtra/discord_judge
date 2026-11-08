import docker
import tempfile
import os
import time

client = docker.from_env()

def run_python_code(source_code: str, memory_limit: str = "256m"):
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "main.py")
        with open(file_path, "w") as f:
            f.write(source_code)
        
        try:
            start_time = time.time()
            
            # Khởi tạo Hộp cát ở chế độ nền (detach=True)
            container = client.containers.run(
                image="python:3.12-alpine",
                command="python /app/main.py",
                volumes={temp_dir: {'bind': '/app', 'mode': 'ro'}},
                working_dir="/app",
                mem_limit=memory_limit,
                network_disabled=True,
                detach=True
            )
            
            try:
                # Chờ code chạy xong
                result = container.wait()
                end_time = time.time()
                
                # Lấy kết quả một cách an toàn
                logs_bytes = container.logs()
                output = logs_bytes.decode("utf-8").strip() if logs_bytes else ""
                
                exit_code = result.get("StatusCode", 0)
                
                if exit_code == 0:
                    return {
                        "status": "Success",
                        "output": output,
                        "runtime": round(end_time - start_time, 3)
                    }
                else:
                    return {
                        "status": "Runtime Error",
                        "output": output,
                        "runtime": round(end_time - start_time, 3)
                    }
            finally:
                # Luôn tự tay tiêu hủy hộp cát
                container.remove(force=True)
                
        except docker.errors.ImageNotFound:
            return {
                "status": "System Error",
                "output": "Chưa tải Image Python về Docker.",
                "runtime": 0
            }
        except Exception as e:
            return {
                "status": "System Error",
                "output": f"Lỗi hệ thống Sandbox: {str(e)}",
                "runtime": 0
            }