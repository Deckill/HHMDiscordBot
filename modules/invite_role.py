import discord
import asyncio
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

invite_cache = {}

# 환경변수에서 초대 코드 → 역할 매핑 로딩
invite_code_to_role = {
    os.getenv("GUILD_INVITATION"): "길드원",
    os.getenv("WORLD_INVITATION"): "손님"
}

async def on_ready(bot):
    for guild in bot.guilds:
        try:
            invites = await guild.invites()
            invite_cache[guild.id] = {invite.code: invite.uses for invite in invites}
            logger.info(f"✅ [{guild.name}] 초대코드 캐시 초기화 완료")
        except discord.Forbidden:
            logger.warning(f"⚠️ [{guild.name}] 초대 링크 권한 없음")

async def on_member_join(member):
    await asyncio.sleep(2)  # 초대 수 반영 대기
    guild = member.guild
    try:
        new_invites = await guild.invites()
    except discord.Forbidden:
        logger.warning(f"⚠️ [{guild.name}] 초대 링크 조회 권한 없음")
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
                logger.info(f"✅ {member.name} → '{role_name}' 역할 부여 완료")
            except discord.Forbidden:
                logger.warning(f"⚠️ {role_name} 역할 부여 실패 (권한 부족)")
        else:
            logger.warning(f"⚠️ {role_name} 역할을 찾을 수 없거나 봇보다 상위 역할임")
    else:
        logger.info(f"ℹ️ {member.name} → 알 수 없는 초대코드 사용")

# bot.py에서 호출되는 초기화 함수
async def initialize(bot):
    bot.add_listener(lambda *_: on_ready(bot), "on_ready")
    bot.add_listener(on_member_join, "on_member_join")
