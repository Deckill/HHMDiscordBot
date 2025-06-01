import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from modules import invite_role, boss_alert
import logging

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)
@bot.event
async def on_ready():
    logger.info(f"✅ {bot.user} 봇 작동 시작!")

# 기능 모듈 등록
invite_role.setup(bot)
boss_alert.setup(bot)

bot.run(os.getenv("DISCORD_TOKEN"))
