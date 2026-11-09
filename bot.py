import discord
from discord.ext import commands
import requests
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
API_URL = "http://127.0.0.1:8000/api"
# KHỞI TẠO BOT
# 1. Cấp quyền cho bot được phép đọc tin nhắn của mọi người
intents = discord.Intents.default()
intents.message_content = True
# 2. Tạo ra con bot và dặn nó: "Chỉ nghe lệnh nào bắt đầu bằng dấu chấm than (!)"
bot = commands.Bot(command_prefix='!', intents=intents)
# SỰ KIỆN KHI BOT TỈNH DẬY
@bot.event
async def on_ready():
    # In ra màn hình đen (Terminal) của BẠN để bạn biết nó đã sống
    print("let coding!!!")


# DẠY BOT CÁCH NHẬN BÀI NỘP
@bot.command()
async def submit(ctx, problem_id: int, *, code: str):
# 1. Bot nhắn lại Discord để người dùng yên tâm chờ đợi
    await ctx.send("Đang cầm code của bạn chạy sang giao cho FastAPI...")
# 2. Đóng gói dữ liệu giống hệt như lúc bạn nộp trên web Swagger UI
    du_lieu = {
        "user_discord_id": str(ctx.author.id), # Lấy ID Discord của người gửi
        "problem_id": problem_id,
        "source_code": code,
        "language": "python"
    }
# 3. Ném gói dữ liệu đó vào địa chỉ của FastAPI (POST)
    ket_qua = requests.post("http://127.0.0.1:8000/api/submissions/", json=du_lieu)
# 4. Rạch gói hàng API trả về để lấy cái mã số bài nộp
    ma_bai_nop = ket_qua.json().get("id")
    await ctx.send(f"Đã nộp xong! Mã bài nộp của bạn là: {ma_bai_nop}")

bot.run(TOKEN)
