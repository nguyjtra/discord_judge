import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
# Khai báo 1 lần dùng mãi mãi
API_URL = "http://127.0.0.1:8000/api"
# KHỞI TẠO BOT
intents = discord.Intents.default()
intents.message_content = True
# Lệnh bắt đầu bằng dấu *
bot = commands.Bot(command_prefix='*', intents=intents)

# SỰ KIỆN KHI BOT TỈNH DẬY
@bot.event
async def on_ready():
    print("let coding!!!")

# LỆNH 1: NHẬN BÀI NỘP
@bot.command()
async def submit(ctx, problem_id: int, *, code: str):
    await ctx.send("Sending Code to FastAPI...")
    
    # Dọn dẹp dấu nháy (```python) nếu người dùng dán code có format trên Discord
    clean_code = code.strip("`")
    if clean_code.startswith("python"):
        clean_code = clean_code[6:].strip()

    du_lieu = {
        "user_discord_id": str(ctx.author.id), 
        "problem_id": problem_id,
        "source_code": clean_code,
        "language": "python"
    }
    
    # Dùng biến API_URL cho gọn và chuẩn
    ket_qua = requests.post(f"{API_URL}/submissions/", json=du_lieu)
    ma_bai_nop = ket_qua.json().get("id")
    
    await ctx.send(f"Success! The submission ID is: {ma_bai_nop}")

# LỆNH 2: HỎI AI GIẢI THÍCH
@bot.command()
async def explain(ctx, submission_id: int):
    await ctx.send(f"AI support #{submission_id}...")
    try:
        ket_qua = requests.get(f"{API_URL}/submissions/{submission_id}/explain")
        if ket_qua.status_code == 200:
            data = ket_qua.json()
            noi_dung = data.get("ai_explanation") or data.get("message") or "No response from AI."
            # Giới hạn 2000 ký tự của Discord
            if len(noi_dung) > 1900:
                noi_dung = noi_dung[:1900] + "\n...(truncated)"
            await ctx.send(noi_dung)
        else:
            await ctx.send(f"Error (HTTP {ket_qua.status_code})")
    except Exception as e:
        await ctx.send("Server connection error.")

# LỆNH 3: BÁO LỖI (TICKET)
@bot.command()
async def ticket(ctx, *, description: str):
    """use this command to report issue : *ticket <.......>"""
    await ctx.send("Sending...")
    
    du_lieu = {
        "user_discord_id": str(ctx.author.id),
        "issue_description": description
    }
    
    try:
        ket_qua = requests.post(f"{API_URL}/tickets/", json=du_lieu)
        
        if ket_qua.status_code == 200:
            ticket_id = ket_qua.json().get("id")
            await ctx.send(f"Your Ticket number is `TICKET-#{ticket_id}`.")
        else:
            await ctx.send("System Error")
            
    except Exception as e:
        await ctx.send("Router problem")

# COMMAND 4: SHOW PROBLEM LIST (*problems)
@bot.command(name='problems')
async def list_problems(ctx):
    await ctx.send("Loading problems...")
    try:
        response = requests.get(f"{API_URL}/problems/")
        if response.status_code == 200:
            problem_list = response.json()
            if not problem_list:
                await ctx.send("No problems found!")
                return
                
            msg = "**PROBLEM LIST:**\n"
            for p in problem_list:
                difficulty = p.get('difficulty', 'Easy')
                msg += f"**#{p['id']}** - {p['title']} (Difficulty: {difficulty})\n"
            await ctx.send(msg)
        else:
            await ctx.send("Failed to get data from server.")
    except Exception as e:
        await ctx.send("Server connection error.")

# COMMAND 5: SHOW PROBLEM DETAILS (*problem <id>)
@bot.command(name='problem')
async def show_problem(ctx, problem_id: int):
    try:
        response = requests.get(f"{API_URL}/problems/{problem_id}")
        if response.status_code == 200:
            p = response.json()
            msg = f"**Problem {p['id']}: {p['title']}**\n"
            msg += f"**Description:**\n{p['description']}\n\n"
            msg += f"*(Type ` *submit {p['id']} <code>` to submit your answer)*"
            await ctx.send(msg)
        elif response.status_code == 404:
            await ctx.send(f"Problem #{problem_id} not found!")
        else:
            await ctx.send("Server error.")
    except Exception as e:
        await ctx.send("Server connection error.")
bot.run(TOKEN)