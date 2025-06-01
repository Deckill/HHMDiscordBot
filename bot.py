import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from modules import invite_role, boss_alert

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} 봇 작동 시작!")
    await invite_role.initialize(bot)
    await boss_alert.initialize(bot)

# 기능 모듈 등록
invite_role.setup(bot)
boss_alert.setup(bot)

bot.run(os.getenv("DISCORD_TOKEN"))
