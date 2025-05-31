import os
import discord
import asyncio
from discord.ext import commands
from flask import Flask
from threading import Thread

# 웹서버 설정 (슬립 방지용)
app = Flask('')

@app.route('/')
def home():
    return "✅ 봇 작동 중입니다!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 디스코드 인텐트
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

invite_cache = {}

# 환경 변수에서 초대 코드 불러오기
guild_invite = os.getenv("GUILD_INVITATION")
world_invite = os.getenv("WORLD_INVITATION")

if not guild_invite or not world_invite:
    print("❌ GUILD_INVITATION 또는 WORLD_INVITATION 환경변수 누락!")
    exit()

invite_code_to_role = {
    guild_invite: "길드원",
    world_invite: "손님"
}

@bot.event
async def on_ready():
    print(f"✅ {bot.user} 봇 작동 시작!")
    for guild in bot.guilds:
        invites = await guild.invites()
        invite_cache[guild.id] = {invite.code: invite.uses for invite in invites}

@bot.event
async def on_member_join(member):
    await asyncio.sleep(2)
    guild = member.guild
    new_invites = await guild.invites()
    old_invites = invite_cache.get(guild.id, {})

    used_code = None
    for invite in new_invites:
        if invite.code in old_invites and invite.uses > old_invites[invite.code]:
            used_code = invite.code
            break

    invite_cache[guild.id] = {invite.code: invite.uses for invite in new_invites}

    if used_code and used_code in invite_code_to_role:
        role = discord.utils.get(guild.roles, name=invite_code_to_role[used_code])
        if role and member.guild.me.top_role > role:
            await member.add_roles(role)
            print(f"{member} → {role.name} 역할 부여")
        else:
            print("⚠️ 역할 부여 실패 (위치 또는 존재 문제)")
    else:
        print(f"{member} → 알 수 없는 초대코드 사용")

# 실행
keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
