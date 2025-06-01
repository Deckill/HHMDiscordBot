# bot.py
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

# ✅ 슬래시 명령어 등록 가능한 봇 클래스
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=intents)
        self.synced = False  # 중복 sync 방지

    async def setup_hook(self):
        await invite_role.initialize(self)
        await boss_alert.initialize(self)

        if not self.synced:
            await self.tree.sync()  # ✅ 슬래시 명령어 전체 동기화
            self.synced = True

bot = MyBot()

# 테스트용 슬래시 명령어
@bot.tree.command(name="테스트", description="슬래시 명령어 작동 확인")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message("✅ 슬래시 명령어 성공!", ephemeral=True)

@bot.event
async def on_ready():
    logger.info(f"✅ {bot.user} 봇 작동 시작!")
    if not boss_alert.check_schedule.is_running():
        boss_alert.check_schedule.start()
    for cmd in bot.tree.walk_commands():
        print(f"🔧 등록된 슬래시 명령어: /{cmd.name} - {cmd.description}")

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
