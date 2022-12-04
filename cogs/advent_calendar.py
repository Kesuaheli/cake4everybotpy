from files import sql as SQL
from os import path
from urllib.request import urlopen
import sys
import random
import json

from bot import Bot

from discord.ext.commands import Cog
from discord import Embed, RawReactionActionEvent
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option

from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, date

months = [("Januar", 31), ("Februar", 29), ("März", 31), ("April", 30), ("Mai", 31), ("Juni", 30),
          ("Juli", 31), ("August", 31), ("September", 30), ("Oktober", 31), ("November", 30), ("Dezember", 31)]
with open(path.join(path.dirname(path.dirname(__file__)), "config.json")) as f:
    guild_id = json.load(f)['base']['guild_id']


class AdventCalendar(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.advent_channel = self.bot.get_channel(1046802329241931806)
        self.today = date.today()

    async def openCalendar(self):
        self.today = date.today()

        if self.today.month != 12 or self.today.day > 24:
            return

        untilCristmas = self.nextDate(24, 12) - self.today
        if untilCristmas.days >= 24 or untilCristmas.days < 0:
            self.bot.log.warning(
                f"Its {untilCristmas.days} days until chritmas eve... skipping")
            msg = f"Noch {untilCristmas.days} mal schlafen bis heilig Abend. Heute öffnet sich das {self.today.day}. Türchen (<- die zweite Zahl stimmt nicht, weil das hier noch ein Test ist. Es wird aber ab 1. Dezember automatisch richtig sein und dann gibts auch diese lange Nachriht nicht mehr xD)"
            self.bot.log.info(msg)
            return
        elif untilCristmas.days == 0:
            msg = "Heute ist Heiligabend :santa:\nZeit für das letzte Türchen für dieses Jahr!"
        else:
            msg = f"Noch {untilCristmas.days} mal schlafen bis heilig Abend. Heute öffnet sich das {self.today.day}. Türchen"

        self.bot.log.info(f"Advent Calendar: Door {self.today.day}")
        image_url = f"https://cake4everyone.de/files/xmas/{self.today.day}.png"
        self.bot.log.info("image: "+image_url)

        adventEmbed = Embed(
            description=msg,
            color=0x2f3136)
        adventEmbed.set_image(url=image_url)
        adventEmbed.set_footer(
            text=f"{self.bot.user.display_name} > Adventskalender", icon_url=self.bot.user.avatar_url)

        self.last_msg = await self.bot.advent_channel.send(embed=adventEmbed)
        await self.last_msg.add_reaction("🎅")

    def nextDate(self, day: int, month: int):
        original_day, original_month = day, month
        if self.today.year % 4 and day == 29 and month == 2:
            day, month = 1, 3
        next_date = date(self.today.year, month, day)

        if next_date < self.today:
            if (self.today.year+1) % 4 and original_day == 29 and original_month == 2:
                day, month = 1, 3
            next_date = date(self.today.year+1, month, day)

        return next_date

    @Cog.listener()
    async def on_ready(self):

        # misfire_grace_time=(15 hours, 59 minutes, 58 seconds) to run latest at 23:59:58 on that day
        self.bot.scheduler.add_job(self.openCalendar, CronTrigger(hour=8), misfire_grace_time=57598)

        self.bot.cogs_ready.ready_up(path.basename(__file__)[:-3])

    @Cog.listener()
    async def on_raw_reaction_add(self, e: RawReactionActionEvent):
        await self.handle_reaction(e)

    @Cog.listener()
    async def on_raw_reaction_remove(self, e: RawReactionActionEvent):
        await self.handle_reaction(e)

    
    @cog_ext.cog_subcommand(base="adventskalender", name="ziehen",
                            base_description="Verschiedene Einstellungen für den Adventskalenderbot.",
                            description="Ziehe einen Gewinner für den Adventskalender.",
                            guild_ids=[guild_id])
    async def drawWinner(self, ctx: SlashContext):
        await ctx.send("WIP.", hidden=True)
    
    @cog_ext.cog_subcommand(base="adventskalender", name="hinzufügen",
                            base_description="Verschiedene Einstellungen für den Adventskalenderbot.",
                            description="Füge eine Person für die Auslosung hinzu.",
                            guild_ids=[guild_id],
                            options=[
                                create_option(name="person",
                                              description="Welche Person möchtest du ins Gewinnspiel aufnehmen?",
                                              option_type=6,
                                              required=True
                                              ),
                                create_option(name="tickets",
                                              description="Wieviele Tickets hat diese Person?",
                                              option_type=4,
                                              required=True,
                                              min_value=0,
                                              max_value=24
                                              )
                            ])
    async def addMember(self, ctx: SlashContext, person, tickets):
        await ctx.send("WIP.", hidden=True)

    async def handle_reaction(self, e: RawReactionActionEvent):
        channel = await self.bot.fetch_channel(e.channel_id)
        
        if channel.id != self.bot.advent_channel.id:
            self.bot.log.debug("not correct channel")
            return

        message = await channel.fetch_message(e.message_id)
        if message.author != self.bot.user:
            self.bot.log.debug("reacted message is not from me")
            return

        if e.emoji.name != "🎅":
            self.bot.log.debug(f"not correct emoji: '{e.emoji}'")
            return

        reactUser = await self.bot.guild.fetch_member(e.user_id)
        if reactUser.bot:
            self.bot.log.debug("reactor is bot")
            return

        dTime = datetime.utcnow() - message.created_at
        timeFormat = f"{int(dTime.total_seconds())//3600}h, {int(dTime.total_seconds())%3600//60}m, {int(dTime.total_seconds())%60}s"
        under16hrs = ":white_check_mark:" if dTime.total_seconds() < 16*3600 else ":x:"
        reaction = next(filter(lambda r: r.emoji == e.emoji.name or r.emoji.name == e.emoji.name, message.reactions), None)

        await self.bot.guild_log.send(
            f"new reaction from {reactUser.mention}: \n> `Type `: `{e.event_type}`\n> `Time `: {timeFormat}\n> `<16h `: {under16hrs}\n> `Count`: {reaction.count}")

def setup(bot: Bot):
    bot.add_cog(AdventCalendar(bot))
