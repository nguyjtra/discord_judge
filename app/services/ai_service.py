import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)


def tim_so_dong_loi(thong_bao_loi: str):
    if not thong_bao_loi:
        return None

    cac_dong_thong_bao = thong_bao_loi.splitlines()
    so_dong_loi = None

    for dong in cac_dong_thong_bao:
        if "line " in dong:
            phan_sau_chu_line = dong.split("line ")[1]
            chuoi_so = phan_sau_chu_line.split(",")[0].strip()

            if chuoi_so.isdigit():
                so_dong_loi = int(chuoi_so)

    return so_dong_loi


def lay_doan_code_loi(source_code: str, thong_bao_loi: str):
    so_dong_loi = tim_so_dong_loi(thong_bao_loi)

    if so_dong_loi is None:
        return source_code

    danh_sach_dong = source_code.splitlines()
    tong_so_dong = len(danh_sach_dong)

    dong_bat_dau = so_dong_loi - 2
    if dong_bat_dau < 1:
        dong_bat_dau = 1

    dong_ket_thuc = so_dong_loi + 2
    if dong_ket_thuc > tong_so_dong:
        dong_ket_thuc = tong_so_dong

    doan_code_ngan = ""
    for so_thu_tu in range(dong_bat_dau, dong_ket_thuc + 1):
        noi_dung_dong = danh_sach_dong[so_thu_tu - 1]

        if so_thu_tu == so_dong_loi:
            doan_code_ngan += f"--> Dòng {so_thu_tu} (BỊ LỖI): {noi_dung_dong}\n"
        else:
            doan_code_ngan += f"    Dòng {so_thu_tu}: {noi_dung_dong}\n"

    return doan_code_ngan


def explain_code_error(source_code: str, error_message: str = None) -> str:
    try:
        doan_code_can_hoi = lay_doan_code_loi(source_code, error_message)

        model = genai.GenerativeModel("gemini-3.5-flash-lite")
        prompt = f"""
        Thông báo lỗi:
        {error_message}

        Đoạn code cần kiểm tra:
        {doan_code_can_hoi}

        Yêu cầu:
        - Trả lời ngắn gọn.
        - Giải thích từng dòng trong đoạn code trên và chỉ ra cách sửa lỗi.
        - Lưu ý: Luôn trả lời bằng tiếng Anh.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"
