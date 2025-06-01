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
    # 환경변수 로드 및 로깅
    guild_invite = os.getenv("GUILD_INVITATION", "").strip()
    world_invite = os.getenv("WORLD_INVITATION", "").strip()

    logger.info(f"🔍 GUILD_INVITATION = '{guild_invite}'")
    logger.info(f"🔍 WORLD_INVITATION = '{world_invite}'")

    invite_code_to_role = {}
    if guild_invite:
        invite_code_to_role[guild_invite] = "길드원"
    if world_invite:
        invite_code_to_role[world_invite] = "손님"

    logger.info(f"✅ 등록된 초대 코드 목록: {invite_code_to_role}")

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

        logger.info(f"[디버그] 사용된 초대코드: {used_code}")
        logger.info(f"[디버그] 등록된 코드: {invite_code_to_role}")

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

async def initialize(bot):
    pass
