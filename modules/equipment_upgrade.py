import discord
from discord import app_commands
import random
import logging

logger = logging.getLogger(__name__)

# 강화 확률표
ENHANCE_PROBABILITIES = {
    0: 100, 1: 100, 2: 100, 3: 100,
    4: 80, 5: 70, 6: 60, 7: 50,
    8: 40, 9: 30, 10: 15, 11: 10,
    12: 7, 13: 5, 14: 3, 15: 1,
    16: 1, 17: 1, 18: 1, 19: 1,
    20: 0  # 최대치
}

async def initialize(bot: discord.Client):
    @bot.tree.command(name="장비강화", description="0~20강까지 장비를 강화해봅니다.")
    @app_commands.describe(level="현재 강화 수치 (0~20)")
    async def enhance(interaction: discord.Interaction, level: int):
        if level < 0 or level > 20:
            await interaction.response.send_message("❌ 강화 수치는 0부터 20 사이여야 합니다.", ephemeral=True)
            return

        if level == 20:
            await interaction.response.send_message("⚠️ 이미 최대 강화 수치입니다.", ephemeral=True)
            return

        success_chance = ENHANCE_PROBABILITIES.get(level, 0)
        roll = random.randint(1, 100)

        result = "성공" if roll <= success_chance else "실패"
        next_level = level + 1 if result == "성공" else level

        message = (
            f"🛠️ 장비 강화 시도!"
            f"현재 수치: +{level}\n"
            f"성공 확률: {success_chance}%\n"
            f"결과: **{result}**\n"
            f"➡️ 최종 수치: +{next_level}"
        )
        await interaction.response.send_message(message)

    await bot.tree.sync()
    logger.info("✅ /장비강화 명령어 동기화 완료")
