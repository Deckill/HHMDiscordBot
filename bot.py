import os
import discord
from dotenv import load_dotenv
import logging
import importlib.util
import glob
import traceback

# 로그 설정
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

# .env 파일 로드
load_dotenv()

# 봇 인텐트 설정
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.invites = True
intents.presences = False

# 디스코드 클라이언트 생성
bot = discord.Client(intents=intents)
bot.tree = discord.app_commands.CommandTree(bot)

# 모듈 자동 로딩 함수
async def load_modules(bot: discord.Client):
    for path in glob.glob("modules/*.py"):
        module_name = os.path.splitext(os.path.basename(path))[0]
        if module_name.startswith("_"):
            continue

        module_path = os.path.abspath(path)
        try:
            spec = importlib.util.spec_from_file_location(f"modules.{module_name}", module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "initialize"):
                await module.initialize(bot)
                logger.info(f"✅ {module_name} 모듈 초기화 완료")
            else:
                logger.warning(f"⚠️ {module_name} 모듈에는 initialize(bot) 함수가 없습니다.")
        except Exception:
            logger.exception(f"❌ {module_name} 모듈 초기화 중 오류 발생")

# 봇 준비 완료 시 실행
@bot.event
async def on_ready():
    logger.info(f"🤖 {bot.user} 봇 작동 시작!")

    await load_modules(bot)

    try:
        await bot.tree.sync()
        logger.info("🌐 슬래시 명령어 동기화 완료")
    except Exception:
        logger.exception("❌ 슬래시 명령어 동기화 실패")

    logger.info("📦 모든 모듈 로딩 완료")

# 실행
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("❌ DISCORD_TOKEN이 .env에 정의되어 있지 않습니다.")
    else:
        bot.run(token)
