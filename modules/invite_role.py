import discord
from discord.ext import commands
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

# .env에서 초대 코드 불러오기
GUILD_INVITATION = os.getenv("GUILD_INVITATION", "").strip()
WORLD_INVITATION = os.getenv("WORLD_INVITATION", "").strip()

invites_before = {}
invite_code_to_role = {}

async def initialize(bot: commands.Bot):
    logger.info("✅ invite_role 모듈 초기화 시작")
    
    if not GUILD_INVITATION or not WORLD_INVITATION:
        logger.warning("⚠️ 환경변수에서 초대코드를 찾을 수 없습니다. GUILD_INVITATION 또는 WORLD_INVITATION 누락")

    invite_code_to_role[GUILD_INVITATION] = "길드원"
    invite_code_to_role[WORLD_INVITATION] = "손님"
    logger.info(f"📌 등록된 코드: {invite_code_to_role}")

    # 서버별 기존 초대코드 저장
    for guild in bot.guilds:
        try:
            invites_before[guild.id] = await guild.invites()
            logger.info(f"✅ {guild.name} 서버의 초대코드 캐싱 완료")
        except discord.Forbidden:
            logger.warning(f"❌ {guild.name} 서버 초대코드 접근 권한 없음")
    
    @bot.event
    async def on_member_join(member: discord.Member):
        try:
            invites_after = await member.guild.invites()
            before = invites_before.get(member.guild.id, [])
            used_code = None

            for invite in invites_after:
                before_invite = next((i for i in before if i.code == invite.code), None)
                if before_invite and invite.uses > before_invite.uses:
                    used_code = invite.code
                    break

            invites_before[member.guild.id] = invites_after
            logger.info(f"[디버그] 사용된 초대코드: {used_code}")
            logger.info(f"[디버그] 등록된 코드: {invite_code_to_role}")

            role_name = invite_code_to_role.get(used_code)
            if not role_name:
                logger.info(f"ℹ️ {member.name} → 알 수 없는 초대코드 사용")
                role_name = "손님"

            role = discord.utils.get(member.guild.roles, name=role_name)
            if role:
                await member.add_roles(role)
                logger.info(f"🎉 {member.name} → 역할 '{role_name}' 부여됨")
            else:
                logger.warning(f"⚠️ 역할 '{role_name}' 이(가) 서버에 없음")

        except Exception as e:
            logger.exception(f"❌ on_member_join 처리 중 오류: {e}")
