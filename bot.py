import os
import discord
import asyncio
from discord.ext import commands

# 디스코드 봇 설정
intents = discord.Intents.default()
intents.members = True  # 필수!
bot = commands.Bot(command_prefix="!", intents=intents)

invite_code_to_role = {
    "GUILD_INVITATION": "길드원",
    "WORLD_INVITATION": "손님"
}

# 서버별 invite 캐시 저장
invite_cache = {}

@bot.event
async def on_ready():
    print(f"✅ {bot.user} 봇 작동 시작!")
    for guild in bot.guilds:
        invites = await guild.invites()
        invite_cache[guild.id] = {invite.code: invite.uses for invite in invites}

@bot.event
async def on_member_join(member):
    await asyncio.sleep(2)  # invite 업데이트를 기다림
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
        role_name = invite_code_to_role[used_code]
        role = discord.utils.get(guild.roles, name=role_name)
        if role and member.guild.me.top_role > role:
            await member.add_roles(role)
            print(f"🎉 {member.name} → '{role.name}' 역할 부여됨 (초대코드: {used_code})")
        else:
            print(f"⚠️ 역할 '{role_name}' 부여 실패: 권한 부족 또는 존재하지 않음")
    else:
        print(f"ℹ️ {member.name} → 알 수 없는 초대 코드 사용")

# 실행
bot.run(os.getenv("DISCORD_TOKEN"))

