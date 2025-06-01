import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

GUILD_ID = 123456789012345678  # 너의 서버 ID로 바꿔줘

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=intents)

    async def setup_hook(self):
        # 슬래시 명령어 서버에만 등록
        self.tree.copy_global_to(guild=discord.Object(id=GUILD_ID))
        await self.tree.sync(guild=discord.Object(id=GUILD_ID))

bot = MyBot()

@bot.tree.command(name="테스트", description="슬래시 명령어 확인", guild=discord.Object(id=GUILD_ID))
async def test(interaction: discord.Interaction):
    await interaction.response.send_message("✅ 슬래시 명령어 작동!", ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} 작동 시작!")

bot.run(os.getenv("DISCORD_TOKEN"))
