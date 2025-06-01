# test_bot.py
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
load_dotenv()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ 봇 로그인됨: {bot.user}")

@bot.event
async def on_message(message):
    print(f"📩 수신된 메시지: {message.content} from {message.author}")
    await bot.process_commands(message)

@bot.command(name="ping")
async def ping(ctx):
    print("✅ !ping 명령어 호출됨")
    await ctx.send("pong!")
bot.run(os.getenv("DISCORD_TOKEN"))

