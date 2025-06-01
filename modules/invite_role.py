import discord
from discord.ext import commands
import asyncio
import os

invite_cache = {}

def setup(bot):
    invite_code_to_role = {
        os.getenv("GUILD_INVITATION"): "길드원",
        os.getenv("WORLD_INVITATION"): "손님"
    }

    @bot.event
    async def on_ready():
        for guild in bot.guilds:
            try:
                invites = await guild.invites()
                invite_cache[guild.id] = {invite.code: invite.uses for invite in invites}
            except discord.Forbidden:
                print(f"⚠️ 초대 링크 권한 없음: {guild.name}")

    @bot.event
    async def on_member_join(member):
        await asyncio.sleep(2)
        guild = member.guild
        try:
            new_invites = await guild.invites()
        except discord.Forbidden:
            print(f"⚠️ {guild.name} 서버에서 초대 링크 조회 권한이 없습니다.")
            return

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
            if role and guild.me.top_role > role:
                try:
                    await member.add_roles(role)
                    print(f"✅ {member.name} → {role_name} 역할 부여")
                except discord.Forbidden:
                    print(f"⚠️ {role_name} 역할 부여 실패 (권한 부족)")
            else:
                print(f"⚠️ {role_name} 역할을 찾을 수 없거나 위치가 문제")
        else:
            print(f"ℹ️ {member.name} → 알 수 없는 초대코드 사용")
