import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
API_URL = "http://127.0.0.1:8000/api"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='*', intents=intents)


class TicketPriorityView(discord.ui.View):
    def __init__(self, user_id: str, description: str):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.description = description

    async def gui_ticket(self, interaction: discord.Interaction, priority: str, thoi_gian: str):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("Only the person who typed the command can select this.", ephemeral=True)
            return

        du_lieu = {
            "user_discord_id": self.user_id,
            "issue_description": self.description,
            "priority": priority
        }

        try:
            ket_qua = requests.post(f"{API_URL}/tickets/", json=du_lieu)
            if ket_qua.status_code == 200:
                ticket_id = ket_qua.json().get("id")
                for item in self.children:
                    item.disabled = True
                await interaction.response.edit_message(
                    content=(
                        f"**Ticket Created:** `TICKET-#{ticket_id}`\n"
                        f"- **Category:** {priority}\n"
                        f"- **Countdown:** {thoi_gian}\n"
                        f"- **Issue:** {self.description}\n"
                        f"*(An email notification has been sent to the Admin)*"
                    ),
                    view=self
                )
            else:
                await interaction.response.send_message("System Error when creating ticket.", ephemeral=True)
        except Exception:
            await interaction.response.send_message("Server connection error.", ephemeral=True)

    @discord.ui.button(label="Priority: System / API (15 mins)", style=discord.ButtonStyle.danger)
    async def chon_priority(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.gui_ticket(interaction, "Priority", "15 minutes")

    @discord.ui.button(label="Necessary: Problem / Code (3 hours)", style=discord.ButtonStyle.primary)
    async def chon_necessary(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.gui_ticket(interaction, "Necessary", "3 hours")


@bot.event
async def on_ready():
    print("let coding!!!")

@bot.command()
async def submit(ctx, problem_id: int, *, code: str):
    await ctx.send("Sending Code to FastAPI...")
    
    clean_code = code.strip("`")
    if clean_code.startswith("python"):
        clean_code = clean_code[6:].strip()

    du_lieu = {
        "user_discord_id": str(ctx.author.id), 
        "problem_id": problem_id,
        "source_code": clean_code,
        "language": "python"
    }
    
    ket_qua = requests.post(f"{API_URL}/submissions/", json=du_lieu)
    if ket_qua.status_code == 200:
        ma_bai_nop = ket_qua.json().get("id")
        await ctx.send(f"Success! The submission ID is: {ma_bai_nop}")
        for _ in range(15):
            await asyncio.sleep(2)
            check = requests.get(f"{API_URL}/submissions/{ma_bai_nop}")
            if check.status_code == 200:
                trang_thai = check.json().get("status")
                if trang_thai not in ("Pending", "Judging", "PENDING", "JUDGING"):
                    user_tag = f"<@{ctx.author.id}>"
                    if trang_thai in ("Accepted", "ACCEPTED"):
                        await ctx.send(f"{user_tag} **#{ma_bai_nop}**: **ACCEPTED**")
                    elif trang_thai in ("Wrong Answer", "WRONG_ANSWER"):
                        await ctx.send(f"{user_tag} **#{ma_bai_nop}**: **WRONG ANSWER.**\n*(`*explain {ma_bai_nop}` for AI assist)*")
                    else:
                        await ctx.send(f"{user_tag} **#{ma_bai_nop}**: **{trang_thai}.**\n*(`*explain {ma_bai_nop}` for AI assist)*")
                    return
        await ctx.send("Timeout waiting for judge result.")
    else:
        await ctx.send("Error when submitting code.")

@bot.command()
async def explain(ctx, submission_id: int):
    await ctx.send(f"AI support #{submission_id}...")
    try:
        ket_qua = requests.get(f"{API_URL}/submissions/{submission_id}/explain")
        if ket_qua.status_code == 200:
            data = ket_qua.json()
            noi_dung = data.get("ai_explanation") or data.get("message") or "No response from AI."
            if len(noi_dung) > 1900:
                noi_dung = noi_dung[:1900] + "\n...(truncated)"
            await ctx.send(noi_dung)
        else:
            await ctx.send(f"Error (HTTP {ket_qua.status_code})")
    except Exception as e:
        await ctx.send("Server connection error.")

@bot.command()
async def ticket(ctx, *, description: str):
    view = TicketPriorityView(user_id=str(ctx.author.id), description=description)
    await ctx.send(
        f"**Please select the priority level for your issue:**\n> {description}",
        view=view
    )

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
