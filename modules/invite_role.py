import os
import logging
from discord.ext import commands
import discord

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)8s] %(message)s"))
logger.addHandler(handler)

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

invite_code_to_role = {
    os.getenv("GUILD_INVITATION", "").strip(): "길드원",
    os.getenv("WORLD_INVITATION", "").strip(): "손님"
}

@bot.event
async def on_ready():
    logger.info(f"✅ {bot.user} 봇 작동 시작!")
    for guild in bot.guilds:
        invites = await guild.invites()
        for invite in invites:
            logger.info(f"🔗 서버 [{guild.name}] 초대코드: {invite.code} → 초대한 사람: {invite.inviter}")

@bot.event
async def on_member_join(member):
    logger.info(f"➡️ {member.name} 입장 감지")
    try:
        invites = await member.guild.invites()
        for invite in invites:
            logger.info(f"[디버그] 초대코드 후보: {invite.code}")

        used_invite = max(invites, key=lambda i: i.uses)
        logger.info(f"[디버그] 사용된 초대코드: {used_invite.code}")
        logger.info(f"[디버그] 등록된 코드: {invite_code_to_role}")

        role_name = invite_code_to_role.get(used_invite.code)
        if role_name:
            role = discord.utils.get(member.guild.roles, name=role_name)
            if role:
                await member.add_roles(role)
                logger.info(f"✅ {member.name} → {role.name} 역할 부여")
            else:
                logger.warning(f"❌ 역할 '{role_name}' 을(를) 찾을 수 없음")
        else:
            logger.info(f"ℹ️ {member.name} → 알 수 없는 초대코드 사용")

    except Exception as e:
        logger.exception(f"🚨 예외 발생 on_member_join: {e}")

def setup(bot):
    bot.add_listener(on_member_join)
    bot.add_listener(on_ready)
    
async def initialize(bot):
    setup(bot)