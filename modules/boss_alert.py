import discord
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

KST = timezone(timedelta(hours=9))
BOSS_TIMES = ['12:00', '18:00', '20:00', '22:00']

channel_id = 1378380187951169546  # 실제 채널 ID로 수정 필요

invite_code_to_role = {}  # 이 모듈에선 사용하지 않음

def get_korea_time():
    return datetime.now(KST).strftime("%H:%M")

def setup(bot):
    @bot.command(name="역할설정")
    async def show_role_menu(ctx):
        embed = discord.Embed(
            title="역할 알림 설정",
            description="버튼을 눌러 알림을 켜거나 끌 수 있습니다.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, view=RoleView())

    async def handle_on_ready():
        bot.add_view(RoleView())
        if not check_schedule.is_running():
            check_schedule.start()
        logger.info("✅ boss_alert 모듈 초기화 완료")

    bot.add_listener(handle_on_ready, "on_ready")

class RoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="결계 알림", style=discord.ButtonStyle.primary, custom_id="barrier_role", emoji="❄️")
    async def barrier_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_name = "결계 알림"
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if not role:
            role = await interaction.guild.create_role(name=role_name, color=discord.Color.blue())
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"{role_name} 제거됨", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"{role_name} 추가됨", ephemeral=True)

    @discord.ui.button(label="필드 보스", style=discord.ButtonStyle.danger, custom_id="boss_role", emoji="🔥")
    async def boss_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_name = "필드 보스"
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if not role:
            role = await interaction.guild.create_role(name=role_name, color=discord.Color.red())
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"{role_name} 제거됨", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"{role_name} 추가됨", ephemeral=True)

def create_embed(type_name, emoji):
    return discord.Embed(
        title=f"{emoji} {type_name} 알림",
        description=f"{type_name}가 시작되었습니다!",
        color=discord.Color.blue() if type_name == "결계" else discord.Color.red()
    ).add_field(name="시간", value=get_korea_time()).set_footer(text="마비노기 모바일")

async def send_notification(notification_type, channel, guild):
    if notification_type == "barrier":
        role = discord.utils.get(guild.roles, name="결계 알림")
        if role and role.members:
            await channel.send(content=f"{role.mention}", embed=create_embed("결계", "🌟"))
    elif notification_type == "boss":
        role = discord.utils.get(guild.roles, name="필드 보스")
        if role and role.members:
            await channel.send(content=f"{role.mention}", embed=create_embed("보스", "🔥"))

@tasks.loop(minutes=1)
async def check_schedule():
    logger.info("디버그 1분 송출")
    now = get_korea_time()
    for guild in check_schedule.bot.guilds:
        channel = check_schedule.bot.get_channel(channel_id)
        if not channel:
            continue
        if now.endswith("0"):
            logger.info("결계 알림 송출")
            await send_notification("barrier", channel, guild)
        if now in BOSS_TIMES:
            await send_notification("boss", channel, guild)

# check_schedule에서 bot 사용을 위한 속성 주입
check_schedule.bot = None
