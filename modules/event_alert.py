import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import os

EVENT_URL = "https://mabinogimobile.nexon.com/News/Events?headlineId=2501"
EVENT_CHANNEL_ID = 1381299937618296902
ALERT_ROLE_NAME = "이벤트 알림"
CACHE_FILE = "event_cache.json"

def load_event_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_event_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

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

        # link = f"https://mabinogimobile.nexon.com/News/Events?headlineId={thread_id}"

        # 종료일 파싱
        try:
            if "~" in date_text:
                end_raw = date_text.split("~")[1]
                # 예: '2025.6.19(목) 오전 5시 59분까지' → '2025.6.19'
                end_date_str = end_raw.split("까지")[0].split("(")[0].strip()
                end_date = datetime.strptime(end_date_str, "%Y.%m.%d").date()
            else:
                end_date = datetime(2999, 12, 31).date()
        except:
            end_date = datetime(2999, 12, 31).date()

        events.append({
            "id": thread_id,
            "title": title,
            # "link": link,
            "end_date": end_date
        })

    return events

class EventAlert(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.known_events = load_event_cache()
        self.check_events.start()

    def cog_unload(self):
        self.check_events.cancel()

    @tasks.loop(minutes=60)
    async def check_events(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(EVENT_CHANNEL_ID)
        if not channel:
            return

        events = parse_events()
        today = datetime.now().date()
        updated_cache = {}

        for event in events:
            eid = event["id"]
            title = event["title"]
            link = event["link"]
            end_date = event["end_date"]

            updated_cache[eid] = {
                "title": title,
                "end_date": end_date.isoformat()
            }

            if eid not in self.known_events:
                role = discord.utils.get(channel.guild.roles, name=ALERT_ROLE_NAME)
                mention = role.mention if role else "@everyone"
                await channel.send(
                    f"{mention}\n📢 새로운 이벤트가 등록되었습니다!\n**{title}**\n🔗 {link}"
                )

            else:
                cached_end = datetime.strptime(self.known_events[eid]["end_date"], "%Y-%m-%d").date()
                if (cached_end - today).days == 1:
                    role = discord.utils.get(channel.guild.roles, name=ALERT_ROLE_NAME)
                    mention = role.mention if role else "@everyone"
                    await channel.send(
                        f"{mention}\n⏰ **{title}** 이벤트가 내일 종료됩니다!\n🔗 {link}"
                    )

        # 만료된 이벤트 제거
        for eid, data in list(self.known_events.items()):
            try:
                end = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
                if end < today:
                    continue  # 삭제됨
            except:
                continue

        self.known_events = updated_cache
        save_event_cache(updated_cache)

    @commands.slash_command(name="이벤트알림설정", description="이벤트 알림 역할을 선택할 수 있는 메시지를 보냅니다.")
    async def setup_event_role(self, ctx):
        role = discord.utils.get(ctx.guild.roles, name=ALERT_ROLE_NAME)
        if not role:
            await ctx.respond(f"'{ALERT_ROLE_NAME}' 역할이 서버에 없습니다. 먼저 역할을 만들어주세요.")
            return

        class EventRoleButton(discord.ui.View):
            @discord.ui.button(label="이벤트 알림 받기", style=discord.ButtonStyle.primary)
            async def give_role(self, button, interaction):
                if role in interaction.user.roles:
                    await interaction.response.send_message("이미 역할이 있습니다.", ephemeral=True)
                else:
                    await interaction.user.add_roles(role)
                    await interaction.response.send_message("이벤트 알림 역할을 부여했어요!", ephemeral=True)

            @discord.ui.button(label="알림 그만 받기", style=discord.ButtonStyle.secondary)
            async def remove_role(self, button, interaction):
                if role in interaction.user.roles:
                    await interaction.user.remove_roles(role)
                    await interaction.response.send_message("이벤트 알림 역할을 제거했어요.", ephemeral=True)
                else:
                    await interaction.response.send_message("역할이 없습니다.", ephemeral=True)

        await ctx.respond("이벤트 알림 역할을 설정하세요!", view=EventRoleButton(), ephemeral=False)

def initialize(bot):
    bot.add_cog(EventAlert(bot))
