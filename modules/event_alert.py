import discord
from discord.ext import tasks
from discord import app_commands
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

EVENT_URL = "https://mabinogimobile.nexon.com/News/Events"
EVENT_CHANNEL_ID = 1381299937618296902
ALERT_ROLE_NAME = "이벤트 알림"
CACHE_FILE = "event_cache.json"

# 캐시 로딩 및 저장
def load_event_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_event_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

# 이벤트 크롤링
def parse_events():
    res = requests.get(EVENT_URL)
    soup = BeautifulSoup(res.text, "html.parser")

    events = []
    items = soup.select(".item-list li")

    for item in items:
        thread_id = item.get("data-threadid", "").strip()
        if not thread_id:
            continue

        title_tag = item.select_one(".title span")
        date_tag = item.select_one(".date span")

        if not (title_tag and date_tag):
            continue

        title = title_tag.text.strip()
        date_text = date_tag.text.strip()
        link = f"https://mabinogimobile.nexon.com/News/Events?headlineId={thread_id}"

        try:
            if "~" in date_text:
                end_raw = date_text.split("~")[1]
                end_date_str = end_raw.split("까지")[0].split("(")[0].strip()
                end_date = datetime.strptime(end_date_str, "%Y.%m.%d").date()
            else:
                end_date = datetime(2999, 12, 31).date()
        except:
            end_date = datetime(2999, 12, 31).date()

        events.append({
            "id": thread_id,
            "title": title,
            "link": link,
            "end_date": end_date
        })

    return events

# 역할 버튼 View
class EventRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="이벤트 알림 받기", style=discord.ButtonStyle.primary)
    async def give_role(self, button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ALERT_ROLE_NAME)
        if not role:
            await interaction.response.send_message("❌ 역할을 찾을 수 없습니다", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("이벤트 알림 역할을 제거했어요.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("이벤트 알림 역할을 부여했어요!", ephemeral=True)

# 이벤트 감시 태스크
event_cache = {}

@tasks.loop(minutes=60)
async def check_event_updates():
    await check_event_updates.bot.wait_until_ready()
    channel = check_event_updates.bot.get_channel(EVENT_CHANNEL_ID)
    if not channel:
        return

    today = datetime.now().date()
    parsed = parse_events()
    updated_cache = {}

    for event in parsed:
        eid = event["id"]
        title = event["title"]
        link = event["link"]
        end_date = event["end_date"]

        updated_cache[eid] = {
            "title": title,
            "end_date": end_date.isoformat()
        }

        if eid not in event_cache:
            role = discord.utils.get(channel.guild.roles, name=ALERT_ROLE_NAME)
            mention = role.mention if role else "@everyone"
            await channel.send(f"{mention}\n📢 새로운 이벤트가 등록되었습니다!\n**{title}**\n🔗 {link}")

        elif event_cache[eid]["end_date"] != "2999-12-31":
            cached_end = datetime.strptime(event_cache[eid]["end_date"], "%Y-%m-%d").date()
            if (cached_end - today).days == 1:
                role = discord.utils.get(channel.guild.roles, name=ALERT_ROLE_NAME)
                mention = role.mention if role else "@everyone"
                await channel.send(f"{mention}\n⏰ **{title}** 이벤트가 내일 종료됩니다!\n🔗 {link}")

    global event_cache
    event_cache = updated_cache
    save_event_cache(event_cache)

# ✅ 여기가 꼭 필요했던 initialize(bot)
async def initialize(bot: discord.Client):
    @bot.tree.command(name="이벤트알림설정", description="이벤트 알림 역할을 선택할 수 있는 메시지를 보냅니다.")
    async def 이벤트알림설정(interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ALERT_ROLE_NAME)
        if not role:
            await interaction.response.send_message("❌ '이벤트 알림' 역할이 서버에 없습니다. 먼저 역할을 생성해주세요.", ephemeral=True)
            return

        await interaction.response.send_message("이벤트 알림 역할을 설정하세요!", view=EventRoleView(), ephemeral=False)

    bot.add_view(EventRoleView())
    check_event_updates.bot = bot
    global event_cache
    event_cache = load_event_cache()

    if not check_event_updates.is_running():
        check_event_updates.start()
