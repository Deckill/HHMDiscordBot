import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging

import modules.invite_role as invite_role
import modules.boss_alert as boss_alert

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)
load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.invites = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logger.info(f"✅ {bot.user} 봇 작동 시작!")

    await invite_role.initialize(bot)
    await boss_alert.initialize(bot)

    if not boss_alert.check_schedule.is_running():
        boss_alert.check_schedule.start()

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("❌ DISCORD_TOKEN이 설정되지 않았습니다.")
    else:
        bot.run(token)
