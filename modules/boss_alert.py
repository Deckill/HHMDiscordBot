import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, timezone
import logging

# 로깅 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

KST = timezone(timedelta(hours=9))
BOSS_TIMES = ['12:00', '18:00', '20:00', '22:00']

TARGET_GUILD_ID = 1375766625164202104
TARGET_CHANNEL_ID = 1378380187951169546

def get_korea_time():
    return datetime.now(KST).strftime("%H:%M")

def create_embed(type_name, emoji):
    return (
        discord.Embed(
            title=f"{emoji} {type_name} 알림",
            description=f"{type_name}가 시작되었습니다!",
            color=discord.Color.blue() if type_name == "결계" else discord.Color.red()
        )
        .add_field(name="시간", value=get_korea_time())
        .set_footer(text="마비노기 모바일")
    )

class RoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="결계 알림", style=discord.ButtonStyle.primary, custom_id="barrier_role", emoji="❄️")
    async def barrier_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_name = "결계 알림"
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if not role:
            role = await interaction.guild.create_role(name=role_name, color=discord.Color.blue())
            logger.info(f"[{interaction.guild.name}] '{role_name}' 역할이 생성됨")

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"{role_name} 제거됨", ephemeral=True)
            logger.info(f"[{interaction.guild.name}] {interaction.user}에게서 '{role_name}' 제거")
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"{role_name} 추가됨", ephemeral=True)
            logger.info(f"[{interaction.guild.name}] {interaction.user}에게 '{role_name}' 추가")

    @discord.ui.button(label="필드 보스", style=discord.ButtonStyle.danger, custom_id="boss_role", emoji="🔥")
    async def boss_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_name = "필드 보스"
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if not role:
            role = await interaction.guild.create_role(name=role_name, color=discord.Color.red())
            logger.info(f"[{interaction.guild.name}] '{role_name}' 역할이 생성됨")

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"{role_name} 제거됨", ephemeral=True)
            logger.info(f"[{interaction.guild.name}] {interaction.user}에게서 '{role_name}' 제거")
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"{role_name} 추가됨", ephemeral=True)
            logger.info(f"[{interaction.guild.name}] {interaction.user}에게 '{role_name}' 추가")

async def send_notification(notification_type, channel, guild):
    role_name = "결계 알림" if notification_type == "barrier" else "필드 보스"
    role = discord.utils.get(guild.roles, name=role_name)
    if not role:
        logger.warning(f"[{guild.name}] 역할 '{role_name}' 없음. 알림 생략")
        return
    if not any(not member.bot for member in role.members):
        logger.info(f"[{guild.name}] '{role_name}' 역할에 유저 없음. 알림 생략")
        return

    embed = create_embed("결계" if notification_type == "barrier" else "보스", "🌟" if notification_type == "barrier" else "🔥")
    await channel.send(content=role.mention, embed=embed)
    logger.info(f"[{guild.name}] '{role_name}' 알림 전송됨")

@tasks.loop(minutes=1)
async def check_schedule():
    now = get_korea_time()
    bot = check_schedule.bot
    logger.info(f"⏰ 알림 체크 시간: {now}")

    for guild in bot.guilds:
        if guild.id != TARGET_GUILD_ID:
            logger.debug(f"[{guild.name}] 대상 서버 아님. 스킵")
            continue

        channel = bot.get_channel(TARGET_CHANNEL_ID)
        if not channel:
            logger.warning(f"[{guild.name}] 채널 ID {TARGET_CHANNEL_ID} 존재하지 않음")
            continue

        if now.endswith(":59"):
            logger.info(f"[{guild.name}] 결계 알림 조건 만족")
            await send_notification("barrier", channel, guild)

        if now in BOSS_TIMES:
            logger.info(f"[{guild.name}] 보스 알림 시간 도달")
            await send_notification("boss", channel, guild)

def setup(bot: commands.Bot):
    @bot.command(name="알림설정")
    async def alert_setup(ctx):
        logger.info(f"[{ctx.guild.name}] {ctx.author}가 !알림설정 호출")
        embed = discord.Embed(
            title="알림 역할 설정",
            description="버튼을 눌러 알림을 켜거나 끌 수 있습니다.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, view=RoleView())

async def initialize(bot: commands.Bot):
    bot.add_view(RoleView())
    check_schedule.bot = bot
    logger.info("📦 boss_alert 모듈 초기화 완료")
