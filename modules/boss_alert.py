import discord
from discord.ext import tasks
from datetime import datetime, timedelta, timezone
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

KST = timezone(timedelta(hours=9))
BOSS_TIMES = ['12:00', '18:00', '20:00', '22:00']

TARGET_GUILD_ID = 1375766625164202104
channel_id = 1378380187951169546

def get_korea_time():
    return datetime.now(KST).strftime("%H:%M")

class RoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="결계 알림", emoji="❄️", style=discord.ButtonStyle.primary, custom_id="barrier_alert")
    async def barrier_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        role_name = "결계 알림"
        role = discord.utils.get(member.guild.roles, name=role_name)
        if not role:
            await interaction.response.send_message("❌ 역할을 찾을 수 없습니다", ephemeral=True)
            return

        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(f"{role_name} 제거됨", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.response.send_message(f"{role_name} 부여됨", ephemeral=True)

    @discord.ui.button(label="필드 보스", style=discord.ButtonStyle.danger, emoji="🔥", custom_id="boss_alert")
    async def boss_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_name = "필드 보스"
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if not role:
            role = await interaction.guild.create_role(name=role_name, color=discord.Color.red())
            logger.info(f"역할 생성됨: {role_name}")

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
        if role and any(not member.bot for member in role.members):
            await channel.send(content=f"{role.mention}", embed=create_embed("결계", "🌟"))
            logger.info("결계 알림 송신됨")
    elif notification_type == "boss":
        role = discord.utils.get(guild.roles, name="필드 보스")
        if role and any(not member.bot for member in role.members):
            await channel.send(content=f"{role.mention}", embed=create_embed("보스", "🔥"))
            logger.info("보스 알림 송신됨")

@tasks.loop(minutes=1)
async def check_schedule():
    now = get_korea_time()
    bot = check_schedule.bot
    logger.info(f"⏰ 지금 시간: {now}")
    for guild in bot.guilds:
        if guild.id != TARGET_GUILD_ID:
            continue
        channel = bot.get_channel(channel_id)
        if not channel:
            continue
        if now.endswith(":59"):
            await send_notification("barrier", channel, guild)
        if now in BOSS_TIMES:
            await send_notification("boss", channel, guild)

async def initialize(bot: discord.Client):
    @bot.tree.command(name="알림설정", description="알림 여행을 설정합니다.")
    async def 알림설정(interaction: discord.Interaction):
        logger.info(f"/알림설정 호출됨 by {interaction.user} in {interaction.guild.name}")
        embed = discord.Embed(
            title="역할 알림 설정",
            description="버튼을 눌러 알림을 켜거나 끌 수 있습니다.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, view=RoleView(), ephemeral=False)

    bot.add_view(RoleView())
    check_schedule.bot = bot
    if not check_schedule.is_running():
        check_schedule.start()

    await bot.tree.sync()
    logger.info("✅ 슬래시 명령어 /알림설정 동기화 완료")
