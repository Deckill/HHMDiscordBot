import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging

# 모듈 가져오기
import modules.invite_role as invite_role
import modules.boss_alert as boss_alert

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)
load_dotenv()

# 디스코드 인텐트 설정
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.invites = True
intents.presences = False

# 봇 초기화 (!로 시작하는 커맨드, 디엠 금지)
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logger.info(f"✅ {bot.user} 봇 작동 시작!")

    # 모듈 초기화
    await invite_role.initialize(bot)
    boss_alert.setup(bot)  # <-- boss_alert의 명령어 등록
    await boss_alert.initialize(bot)

    # 일정 알림 루프 시작
    if not boss_alert.check_schedule.is_running():
        boss_alert.check_schedule.start()

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if token is None:
        logger.error("❌ DISCORD_TOKEN이 .env에 정의되어 있지 않습니다.")
    else:
        bot.run(token)
