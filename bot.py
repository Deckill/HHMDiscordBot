import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# from keep_alive import keep_alive
from modules import invite_role, boss_alert

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# 기능 모듈 등록
invite_role.setup(bot)
boss_alert.setup(bot)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} 봇 작동 시작!")

# 실행
# keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
