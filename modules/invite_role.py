import os
import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

invite_cache = {}

# 환경변수에서 초대코드 → 역할 이름 매핑 생성
def get_invite_code_mapping():
    mapping = {}
    guild_invite = os.getenv("GUILD_INVITATION", "").strip().replace('"', '')
    world_invite = os.getenv("WORLD_INVITATION", "").strip().replace('"', '')

    if guild_invite:
        mapping[guild_invite] = "길드원"
    if world_invite:
        mapping[world_invite] = "손님"

    return mapping

invite_code_to_role = get_invite_code_mapping()

def setup(bot):
    @bot.event
    async def on_ready():
        logger.info("🔄 초대 캐시 초기화 중...")
        for guild in bot.guilds:
            try:
                invites = await guild.invites()
                invite_cache[guild.id] = invites
                logger.info(f"✅ {guild.name}({guild.id}) - {len(invites)}개 초대코드 캐시 완료")
            except Exception as e:
                logger.warning(f"⚠️ {guild.name}({guild.id}) - 초대코드 캐시 실패: {e}")

    @bot.event
    async def on_member_join(member):
        guild = member.guild
        try:
            new_invites = await guild.invites()
            old_invites = invite_cache.get(guild.id, [])

            old_invite_map = {invite.code: invite.uses for invite in old_invites}
            used_code = None

            logger.info("[디버그] 초대코드 후보:")
            for invite in new_invites:
                old_uses = old_invite_map.get(invite.code, 0)
                logger.info(f"[디버그] {invite.code} - 이전: {old_uses}, 현재: {invite.uses}")
                if invite.uses > old_uses:
                    used_code = invite.code
                    break

            logger.info(f"[디버그] 사용된 초대코드: {used_code}")
            logger.info(f"[디버그] 등록된 코드: {invite_code_to_role}")

            if used_code and used_code in invite_code_to_role:
                role_name = invite_code_to_role[used_code]
                role = discord.utils.get(guild.roles, name=role_name)
                if role:
                    await member.add_roles(role)
                    logger.info(f"✅ {member.name} → 역할 '{role_name}' 부여")
                else:
                    logger.warning(f"⚠️ 역할 '{role_name}'을(를) 찾을 수 없음")
            else:
                logger.info(f"ℹ️ {member.name} → 알 수 없는 초대코드 사용")

            invite_cache[guild.id] = new_invites

        except Exception as e:
            logger.error(f"❌ on_member_join 오류: {e}")
