import os
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

# .env 로컬 환경에서 테스트용, GCP에서는 시스템 환경변수 사용 가능
load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

invite_cache = {}

# 초대 코드별 자동 역할 매핑
GUILD_INVITATION = os.getenv("GUILD_INVITATION")
WORLD_INVITATION = os.getenv("WORLD_INVITATION")
invite_code_to_role = {
    GUILD_INVITATION: "길드원",
    WORLD_INVITATION: "손님"
}

@bot.event
async def on_ready():
    print(f"✅ {bot.user} 봇 작동 시작!")
    for guild in bot.guilds:
        try:
            invites = await guild.invites()
            invite_cache[guild.id] = {invite.code: invite.uses for invite in invites}
        except discord.Forbidden:
            print(f"❌ 권한 부족으로 {guild.name}에서 초대 코드 정보를 불러올 수 없습니다.")

@bot.event
async def on_member_join(member):
    await asyncio.sleep(2)
    guild = member.guild
    try:
        new_invites = await guild.invites()
    except discord.Forbidden:
        print("❌ 초대 정보를 불러올 수 있는 권한이 없습니다.")
        return

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
            print(f"✅ {member.name}에게 '{role.name}' 역할 부여됨")
        else:
            print("⚠️ 역할 부여 실패 (역할이 없거나 봇 권한 부족)")
    else:
        print(f"ℹ️ {member.name} → 알 수 없는 초대 코드 사용")

# 실행
if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
