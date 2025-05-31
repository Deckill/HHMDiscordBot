import os
import discord
import asyncio

invite_cache = {}
invite_code_to_role = {
    os.getenv("GUILD_INVITATION"): "길드원",
    os.getenv("WORLD_INVITATION"): "손님"
}

def setup(bot):
    @bot.event
    async def on_ready():
        for guild in bot.guilds:
            invites = await guild.invites()
            invite_cache[guild.id] = {invite.code: invite.uses for invite in invites}

    @bot.event
    async def on_member_join(member):
        await asyncio.sleep(2)
        guild = member.guild
        new_invites = await guild.invites()
        old_invites = invite_cache.get(guild.id, {})

        used_code = None
        for invite in new_invites:
            if invite.code in old_invites and invite.uses > old_invites[invite.code]:
                used_code = invite.code
                break

        invite_cache[guild.id] = {invite.code: invite.uses for invite in new_invites}

        if used_code and used_code in invite_code_to_role:
            role = discord.utils.get(guild.roles, name=invite_code_to_role[used_code])
            if role and member.guild.me.top_role > role:
                await member.add_roles(role)
                print(f"{member} → {role.name} 역할 부여")
