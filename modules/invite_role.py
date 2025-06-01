import discord
import asyncio
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)
invite_cache = {}
load_dotenv()

def setup(bot):
    invite_code_to_role = {
        os.getenv("GUILD_INVITATION"): "길드원",
        os.getenv("WORLD_INVITATION"): "손님"
    }

    async def handle_on_ready():
        for guild in bot.guilds:
            try:
                invites = await guild.invites()
                invite_cache[guild.id] = {invite.code: invite.uses for invite in invites}
            except discord.Forbidden:
                logger.info(f"⚠️ 초대 링크 권한 없음: {guild.name}")

    async def handle_on_member_join(member):
        await asyncio.sleep(2)  # 초대 수 반영 딜레이
        guild = member.guild
        try:
            new_invites = await guild.invites()
        except discord.Forbidden:
            logger.info(f"⚠️ {guild.name} 서버에서 초대 링크 조회 권한이 없습니다.")
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
                    logger.info(f"✅ {member.name} → {role_name} 역할 부여")
                except discord.Forbidden:
                    logger.info(f"⚠️ {role_name} 역할 부여 실패 (권한 부족)")
            else:
                logger.info(f"⚠️ {role_name} 역할을 찾을 수 없거나 위치가 문제")
        else:
            logger.info(f"ℹ️ {member.name} → 알 수 없는 초대코드 사용")

    bot.add_listener(handle_on_ready, "on_ready")
    bot.add_listener(handle_on_member_join, "on_member_join")

# 🔧 필수: bot.py 에서 await invite_role.initialize(bot) 호출 시 필요
async def initialize(bot):
    pass
