import os
import discord
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
intents.presences = False

# 슬래시 명령어 전용 클라이언트
bot = discord.Client(intents=intents)
bot.tree = discord.app_commands.CommandTree(bot)

@bot.event
async def on_ready():
    logger.info(f"✅ {bot.user} 봇 작동 시작!")

    await invite_role.initialize(bot)
    await boss_alert.initialize(bot)

    logger.info("🌐 모든 모듈 초기화 완료")

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if token is None:
        logger.error("❌ DISCORD_TOKEN이 .env에 정의되어 있지 않습니다.")
    else:
        bot.run(token)
