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
intents.presences = False

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_message(message):
    logger.info(f"📩 수신된 메시지: {message.content} (from {message.author})")
    await bot.process_commands(message)  # 이 줄을 꼭 넣어야 명령어가 처리됨

@bot.event
async def on_ready():
    logger.info(f"✅ {bot.user} 봇 작동 시작!")

    # 각 모듈 초기화
    await invite_role.initialize(bot)
    await boss_alert.initialize(bot)
    await bot.tree.sync(guild=discord.Object(id=1375766625164202104))

    # 루프 시작은 봇이 완전히 켜진 이후에만!
    if not boss_alert.check_schedule.is_running():
        boss_alert.check_schedule.start()

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
