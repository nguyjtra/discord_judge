import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Tải các biến môi trường từ file .env vào hệ thống
load_dotenv()

# 2. Cấu hình Gemini bằng API Key
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def explain_code_error(source_code: str) -> str:
    """
    Hàm này nhận đoạn code bị lỗi, tạo Prompt và nhờ AI giải thích.
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Khung Prompt chuẩn mực (đóng vai chuyên gia)
        prompt = f"""
        Bạn là một chuyên gia IT và một gia sư lập trình nhiệt huyết.
        Học viên vừa nộp đoạn code Python này vào hệ thống và bị báo lỗi RUNTIME_ERROR:
        {source_code}

        Hãy trả lời tôi theo đúng format sau:
        1. Giải thích nguyên nhân gốc rễ (ngắn gọn, đi thẳng vào vấn đề).
        2. Chỉ ra dòng code bị sai cụ thể.
        3. Đưa ra code đã sửa đúng.
        4. Dặn dò một mẹo nhỏ để tránh lỗi tương tự.

        Lưu ý: Luôn trả lời bằng Anh và gỉai thích Đơn giản cho 1 đứa trẻ 5 tuổi.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Error: {e}"