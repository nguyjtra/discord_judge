import docker
import tempfile
import os
import time

client = docker.from_env()

def run_python_code(source_code: str, input_data: str = "", memory_limit: str = "256m"):
    with tempfile.TemporaryDirectory() as thu_muc_tam:
        duong_dan_file_code = os.path.join(thu_muc_tam, "main.py")
        with open(duong_dan_file_code, "w") as file_code:
            file_code.write(source_code)
            
        duong_dan_file_input = os.path.join(thu_muc_tam, "input.txt")
        with open(duong_dan_file_input, "w") as file_input:
            file_input.write(input_data)
        
        try:
            bat_dau_bam_gio = time.time()
            
            hop_cat = client.containers.run(
                image="python:3.12-alpine",
                command='sh -c "python /app/main.py < /app/input.txt"',
                volumes={thu_muc_tam: {'bind': '/app', 'mode': 'ro'}},
                working_dir="/app",
                mem_limit=memory_limit,
                network_disabled=True,
                detach=True
            )
            
            try:
                ket_qua_thi = hop_cat.wait()
                thoi_gian_lam_bai = round(time.time() - bat_dau_bam_gio, 3)
                
                du_lieu_in_ra = hop_cat.logs()
                
                if du_lieu_in_ra:
                    chuoi_ket_qua = du_lieu_in_ra.decode("utf-8").strip()
                else:
                    chuoi_ket_qua = ""
                
                ma_loi = ket_qua_thi.get("StatusCode", 0)
                
                if ma_loi == 0:
                    return {"status": "Success", "output": chuoi_ket_qua, "runtime": thoi_gian_lam_bai}
                else:
                    return {"status": "Runtime Error", "output": chuoi_ket_qua, "runtime": thoi_gian_lam_bai}
                    
            finally:
                hop_cat.remove(force=True)
                
        except Exception as loi_he_thong:
            return {"status": "System Error", "output": f"Lỗi hệ thống: {str(loi_he_thong)}", "runtime": 0}
