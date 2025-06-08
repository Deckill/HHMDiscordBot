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

RUNE_UPGRADE_PROBABILITIES = {
    0: ("고급 (★0)", 90.0),
    1: ("고급 (★1)", 85.0),
    2: ("레어 (★2)", 80.0),
    3: ("레어 (★3)", 50.0),
    4: ("엘리트 (★4)", 40.0),
    5: ("에픽 (★5)", 10.0),
}

async def initialize(bot: discord.Client):
    @bot.tree.command(name="각인강화", description="0~20강까지 각인를 강화해봅니다.")
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
            f"🛠️ 각인 강화 시도!\n"
            f"현재 수치: +{level}\n"
            f"성공 확률: {success_chance}%\n"
            f"결과: **{result}**\n"
            f"➡️ 최종 수치: +{next_level}"
        )
        await interaction.response.send_message(message)

    @bot.tree.command(name="룬승급", description="룬의 등급을 승급해봅니다 (★0~5).")
    @app_commands.describe(level="현재 레벨 (0~5)")
    async def rune_upgrade(interaction: discord.Interaction, level: int):
        if level < 0 or level > 5:
            await interaction.response.send_message("❌ 승급 레벨은 0부터 5 사이여야 합니다.", ephemeral=True)
            return

        rarity_name, success_chance = RUNE_UPGRADE_PROBABILITIES[level]
        roll = random.uniform(0, 100)
        result = "성공" if roll <= success_chance else "실패"
        next_level = level + 1 if result == "성공" and level < 5 else level
        next_rarity = RUNE_UPGRADE_PROBABILITIES.get(next_level, ("최대치",))[0]

        message = (
            f"🔷 룬 승급 시도!\n"
            f"현재 등급: {rarity_name}\n"
            f"성공 확률: {success_chance:.2f}%\n"
            f"결과: **{result}**\n"
            f"➡️ 최종 등급: {next_rarity}"
        )
        await interaction.response.send_message(message)

    # await bot.tree.sync()
    # logger.info("✅ /각인강화 및 /룬승급 명령어 동기화 완료")
