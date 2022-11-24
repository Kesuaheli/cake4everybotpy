from files import sql as SQL
from os import path
from urllib.request import urlopen
import sys
import random
import json

from bot import Bot

from discord.ext.commands import Cog
from discord import Embed
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option

from apscheduler.triggers.cron import CronTrigger
from datetime import date

months = [("Januar", 31), ("Februar", 29), ("März", 31), ("April", 30), ("Mai", 31), ("Juni", 30),
          ("Juli", 31), ("August", 31), ("September", 30), ("Oktober", 31), ("November", 30), ("Dezember", 31)]
with open(path.join(path.dirname(path.dirname(__file__)), "config.json")) as f:
    guild_id = json.load(f)['base']['guild_id']


class AdventCalendar(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.today = date.today()

    async def openCalendar(self):
        self.today = date.today()

        if self.today.month != 12 or self.today.day > 24:
            return

        self.bot.log.info(f"Advent Calendar: Door {self.today.day}")

        image_url = f"https://cake4everyone.de/files/xmas/{self.today.day}.png"
        self.bot.log.info("image: "+image_url)

        untilCristmas = self.nextDate(24, 12) - self.today
        if untilCristmas.days >= 24 or untilCristmas.days < 0:
            self.bot.log.warning(
                f"Its {untilCristmas.days} days until Chritmas... skipping")
            return
        elif untilCristmas.days == 0:
            msg = "Heute ist Heiligabend :santa:\nZeit für das letzte Türchen für dieses Jahr!"
        else:
            msg = f"Heute öffnet sich das {self.today.day}. Türchen"

        adventEmbed = Embed(
            description=msg,
            color=0x2f3136)
        adventEmbed.set_image(url=image_url)
        adventEmbed.set_footer(
            text=f"{self.bot.user.display_name} > Adventskalender", icon_url=self.bot.user.avatar_url)
        self.last_msg = await self.bot.stdout.send(embed=adventEmbed)
        await self.last_msg.add_reaction(":santa:")

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

        # misfire_grace_time=(16 hours, 59 minutes, 58 seconds) to run latest at 23:59:58 on that day
        self.bot.scheduler.add_job(self.openCalendar, CronTrigger(month=11,
                                                                  hour=8), misfire_grace_time=61198)

        self.bot.cogs_ready.ready_up(path.basename(__file__)[:-3])


def setup(bot: Bot):
    bot.add_cog(AdventCalendar(bot))
