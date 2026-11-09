import docker
import tempfile
import os
import time

# Khởi động "Người quản lý phòng thi" (Docker)
client = docker.from_env()

def run_python_code(source_code: str, input_data: str = "", memory_limit: str = "256m"):
    
    # BƯỚC 1: CHUẨN BỊ PHÒNG THI (Tạo thư mục tạm thời)
    # tempfile giúp tạo ra một "bàn nháp". Khi ra khỏi khối 'with' này,
    #  bàn nháp tự động bị đốt bỏ, không để lại rác trên máy tính.
    with tempfile.TemporaryDirectory() as thu_muc_tam:
        
        # 1.1 - Viết code của học sinh ra một tờ giấy tên là 'main.py'
        duong_dan_file_code = os.path.join(thu_muc_tam, "main.py")
        with open(duong_dan_file_code, "w") as file_code:
            file_code.write(source_code)
            
        # 1.2 - Viết dữ liệu đầu vào (Test Case) ra một tờ giấy tên là 'input.txt'
        duong_dan_file_input = os.path.join(thu_muc_tam, "input.txt")
        with open(duong_dan_file_input, "w") as file_input:
            file_input.write(input_data)
        
        # BƯỚC 2: GỌI GIÁM THỊ VÀ BẮT ĐẦU THI
        try:
            bat_dau_bam_gio = time.time()
            
            # Nhốt code vào Hộp cát sắt (Container)
            # Lệnh 'sh -c' bên dưới nghĩa là: "Hãy chạy file main.py, và mỗi khi code đòi nhập dữ liệu, hãy bốc từ file input.txt bỏ vào"
            hop_cat = client.containers.run(
                image="python:3.12-alpine",
                command='sh -c "python /app/main.py < /app/input.txt"',
                volumes={thu_muc_tam: {'bind': '/app', 'mode': 'ro'}}, # Đưa 2 tờ giấy vào phòng thi (chỉ đọc)
                working_dir="/app",
                mem_limit=memory_limit,
                network_disabled=True, # Rút dây mạng, cấm gian lận
                detach=True            # Cho chạy ngầm
            )
            
            # BƯỚC 3: THU BÀI VÀ CHẤM ĐIỂM
            try:
                # Ngồi đợi học sinh làm bài xong
                ket_qua_thi = hop_cat.wait()
                thoi_gian_lam_bai = round(time.time() - bat_dau_bam_gio, 3)
                
                # Thu lại tờ giấy nháp ghi kết quả trên màn hình (Logs)
                du_lieu_in_ra = hop_cat.logs()
                
                # Ép dữ liệu máy tính thành chữ người đọc được (giải mã utf-8), và xóa khoảng trắng dư thừa (.strip)
                if du_lieu_in_ra:
                    chuoi_ket_qua = du_lieu_in_ra.decode("utf-8").strip()
                else:
                    chuoi_ket_qua = ""
                
                # StatusCode = 0 nghĩa là code chạy êm xuôi. Bất kỳ số nào khác 0 đều là bị lỗi (chia cho 0, gõ sai tên biến...)
                ma_loi = ket_qua_thi.get("StatusCode", 0)
                
                if ma_loi == 0:
                    return {"status": "Success", "output": chuoi_ket_qua, "runtime": thoi_gian_lam_bai}
                else:
                    return {"status": "Runtime Error", "output": chuoi_ket_qua, "runtime": thoi_gian_lam_bai}
                    
            # BƯỚC 4: DỌN DẸP PHÒNG THI (Bắt buộc phải làm dù code chạy đúng hay lỗi)
            finally:
                hop_cat.remove(force=True) # Xóa sạch Hộp cát, trả lại RAM cho máy Mac của bạn
                
        # Bắt các lỗi hi hữu của hệ thống (ví dụ: quên chưa tải ảnh Python về máy)
        except Exception as loi_he_thong:
            return {"status": "System Error", "output": f"Lỗi hệ thống: {str(loi_he_thong)}", "runtime": 0}