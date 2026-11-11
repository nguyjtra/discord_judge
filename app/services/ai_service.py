import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Tải các biến môi trường từ file .env vào hệ thống
load_dotenv()

# 2. Cấu hình Gemini bằng API Key
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def explain_code_error(source_code: str) -> str:
    try:
        model = genai.GenerativeModel("gemini-3.5-flash-lite")
        prompt = f"""
        {source_code}
        trả lời ngắn gọn
        và giải thích từng dòng code 
        Lưu ý: Luôn trả lời bằng Anh và gỉai thích Đơn giản cho 1 đứa trẻ 5 tuổi.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Error: {e}"