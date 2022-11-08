from files import sql as SQL
from os import path
from urllib.request import urlopen
import sys
import random
import json

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


class Birthday(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.today = date.today()
        self.members = []
        self.google_apiKey = ""
        self.google_searchEngine = ""
        self.google_baseUrl = "https://www.googleapis.com/customsearch/v1?num={count}&start={startIndex}&key={apiKey}&cx={searchEngine}&q={querry}&searchType=image"

    @cog_ext.cog_subcommand(base="geburtstag", name="eintragen",
                            description="Trage deinen Geburtstag ein oder aktualisiere ihn.",
                            base_description="Verschiedene Einstellungen für den Geburtstagsbot.",
                            guild_ids=[guild_id],
                            options=[
                                create_option(name="tag",
                                              description="An welchem Tag im Monat hast du Geburtstag?",
                                              option_type=4,
                                              required=True,
                                              min_value=1,
                                              max_value=31
                                              ),
                                create_option(name="monat",
                                              description="In welchem Monat hast du Geburtstag?",
                                              option_type=4,
                                              required=True,
                                              choices=[
                                                  create_choice(
                                                      name="Januar",    value=1),
                                                  create_choice(
                                                      name="Februar",   value=2),
                                                  create_choice(
                                                      name="März",      value=3),
                                                  create_choice(
                                                      name="April",     value=4),
                                                  create_choice(
                                                      name="Mai",       value=5),
                                                  create_choice(
                                                      name="Juni",      value=6),
                                                  create_choice(
                                                      name="Juli",      value=7),
                                                  create_choice(
                                                      name="August",    value=8),
                                                  create_choice(
                                                      name="September", value=9),
                                                  create_choice(
                                                      name="Oktober",   value=10),
                                                  create_choice(
                                                      name="November",  value=11),
                                                  create_choice(
                                                      name="Dezember",  value=12)
                                              ]
                                              ),
                                create_option(name="liste",
                                              description="Soll dein Name und Geburtstag in der Suchliste angezeigt werden? (Standard ist \"Ja\")",
                                              option_type=3,
                                              required=False,
                                              choices=[
                                                  create_choice(
                                                      name="Ja",    value="ja"),
                                                  create_choice(
                                                      name="Nein",  value="nein")
                                              ]
                                              )
                            ])
    async def add(self, ctx: SlashContext, tag, monat, liste="ja"):
        newDay, newMonth = tag, monat
        if liste == "ja":
            newShow = True
        else:
            newShow = False
        getDay = None
        try:
            getDay, getMonth, getName, getDiscriminator, getNick, getShow = SQL.execute(
                f"SELECT day,month,username,discriminator,nickname,show FROM birthdays WHERE id={ctx.author.id}").fetchall()[0]
        except IndexError:
            pass
        if newDay > months[newMonth-1][1]:
            placeholder = "eingetragen"
            if getDay:
                placeholder = "aktualisiert"
            birthdayEmbed = Embed(
                title=f"Geburtstag konnte nicht {placeholder} werden!",
                description=f"**Der {months[newMonth-1][0]} hat keine {newDay} Tage.**",
                color=0xe62417)
            birthdayEmbed.set_author(
                name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            birthdayEmbed.set_footer(
                text=f"{self.bot.user.display_name} > Geburtstag", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=birthdayEmbed, hidden=True)
            return
        if getDay:
            if newDay is not getDay:
                SQL.execute(
                    f"UPDATE birthdays SET day = {newDay} WHERE id = {ctx.author.id}")
            if newMonth is not getMonth:
                SQL.execute(
                    f"UPDATE birthdays SET month = {newMonth} WHERE id = {ctx.author.id}")
            if ctx.author.name is not getName:
                SQL.execute(
                    f"UPDATE birthdays SET username = '{ctx.author.name}' WHERE id = {ctx.author.id}")
            if ctx.author.discriminator is not getDiscriminator:
                SQL.execute(
                    f"UPDATE birthdays SET discriminator = {ctx.author.discriminator} WHERE id = {ctx.author.id}")
            if ctx.author.nick is not getNick:
                SQL.execute(
                    f"UPDATE birthdays SET nickname = '{ctx.author.nick}' WHERE id = {ctx.author.id}")
            elif not ctx.author.nick and getNick:
                SQL.execute(
                    f"UPDATE birthdays SET nickname = NULL WHERE id = {ctx.author.id}")
            if newShow is not getShow:
                SQL.execute(
                    f"UPDATE birthdays SET show = {newShow} WHERE id = {ctx.author.id}")
            birthdayEmbed = Embed(
                title="Geburtstag aktualisiert!",
                description=f"Geburtstag am **{tag}. {months[newMonth-1][0]}**",
                color=0xc59e25)
            birthdayEmbed.set_author(
                name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            birthdayEmbed.set_footer(
                text=f"{self.bot.user.display_name} > Geburtstag", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=birthdayEmbed)
        else:
            birthdayEmbed = Embed(
                title="Geburtstag eingetragen!",
                description=f"Geburtstag am **{tag}. {months[newMonth-1][0]}**",
                color=0x00ff00)
            birthdayEmbed.set_author(
                name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            birthdayEmbed.set_footer(
                text=f"{self.bot.user.display_name} > Geburtstag", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=birthdayEmbed)

            if ctx.author.nick:
                SQL.execute(
                    f"INSERT INTO birthdays (id, day, month, username, discriminator, nickname, show) VALUES ({ctx.author.id}, {newDay}, {newMonth}, '{ctx.author.name}', {ctx.author.discriminator}, '{ctx.author.nick}', {newShow})")
            else:
                SQL.execute(
                    f"INSERT INTO birthdays (id, day, month, username, discriminator, show) VALUES ({ctx.author.id}, {newDay}, {newMonth}, '{ctx.author.name}', {ctx.author.discriminator}, {newShow})")

        SQL.commit()

    @cog_ext.cog_subcommand(base="geburtstag", name="löschen",
                            description="Streiche deinen Geburtstag aus dem Kalender",
                            base_description="Verschiedene Einstellungen für den Geburtstagsbot.",
                            guild_ids=[guild_id]
                            )
    async def remove(self, ctx: SlashContext):
        hasBirthday = bool(SQL.execute_one(
            f"SELECT EXISTS (SELECT NULL FROM birthdays WHERE id={ctx.author.id})"))
        if hasBirthday:
            SQL.execute(
                f"DELETE FROM birthdays WHERE id = {ctx.author.id}", commit=True)
            birthdayEmbed = Embed(
                title="Geburtstag gelöscht!",
                description=f"Dein Geburtstag wurde aus dem Kalender gestrichen.",
                color=0x00ff00)
            birthdayEmbed.set_author(
                name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            birthdayEmbed.set_footer(
                text=f"{self.bot.user.display_name} > Geburtstag", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=birthdayEmbed)
        else:
            birthdayEmbed = Embed(
                title="Geburtstag konnte nicht gelöscht werden!",
                description="**Du hast keinen Geburtstag im Kalender stehen.**",
                color=0xe62417)
            birthdayEmbed.set_author(
                name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            birthdayEmbed.set_footer(
                text=f"{self.bot.user.display_name} > Geburtstag", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=birthdayEmbed, hidden=True)

    @cog_ext.cog_subcommand(base="geburtstag", subcommand_group="liste", name="person",
                            base_description="Verschiedene Einstellungen für den Geburtstagsbot.",
                            subcommand_group_description="Zeige Geburtstage.",
                            description="Zeige den Geburtstag von einer bestimmten Person.",
                            guild_ids=[guild_id],
                            options=[
                                create_option(name="person",
                                              description="Von welcher Person möchtest du den Geburtstag wissen?",
                                              option_type=6,
                                              required=True
                                              )
                            ])
    async def listMember(self, ctx: SlashContext, person):
        cmdMember = person

        day = None
        try:
            day, month, show = SQL.execute(
                f"SELECT day, month, show FROM birthdays WHERE id={cmdMember.id}").fetchall()[0]
        except IndexError:
            pass

        if not day or not bool(show):
            listEmbed = Embed(
                title=f"Geburtstag von {cmdMember.display_name}",
                description=f"**{cmdMember.display_name} hat keinen Geburtstag eingetragen oder ihn nicht als gelistet markiert!**",
                color=0xe62417
            )
            listEmbed.set_footer(
                text=f"{self.bot.user.display_name} > Geburtstag", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=listEmbed, hidden=True)
        else:
            listEmbed = Embed(
                title=f"Geburtstag von {cmdMember.display_name}",
                color=0x00ff00
            )

            self.today = date.today()
            delta_t = self.nextDate(day, month) - self.today
            if delta_t.days == 0:
                relative = "Heute :partying_face:"
            elif delta_t.days == 1:
                relative = "Morgen :shushing_face:"
            elif delta_t.days == 69:
                relative = "In **69** Tagen. Nice!"
            elif delta_t.days == 100:
                relative = "In :100: Tagen"
            else:
                relative = f"In {delta_t.days} Tagen"

            listEmbed.add_field(
                name=f"{day}. {months[month-1][0]}", value=relative)
            listEmbed.set_author(name=cmdMember.display_name,
                                 icon_url=cmdMember.avatar_url)
            listEmbed.set_footer(
                text=f"{self.bot.user.display_name} > Geburtstag", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=listEmbed)

    @cog_ext.cog_subcommand(base="geburtstag", subcommand_group="liste", name="monat",
                            base_description="Verschiedene Einstellungen für den Geburtstagsbot.",
                            subcommand_group_description="Zeige Geburtstage.",
                            description="Zeige alle Geburtstag aus einem bestimmten Monat.",
                            guild_ids=[guild_id],
                            options=[
                                create_option(name="monat",
                                              description="Für welchen Monat möchtest du die Geburtstage anzeigen?",
                                              option_type=4,
                                              required=True,
                                              choices=[
                                                  create_choice(
                                                      name="Januar",    value=1),
                                                  create_choice(
                                                      name="Februar",   value=2),
                                                  create_choice(
                                                      name="März",      value=3),
                                                  create_choice(
                                                      name="April",     value=4),
                                                  create_choice(
                                                      name="Mai",       value=5),
                                                  create_choice(
                                                      name="Juni",      value=6),
                                                  create_choice(
                                                      name="Juli",      value=7),
                                                  create_choice(
                                                      name="August",    value=8),
                                                  create_choice(
                                                      name="September", value=9),
                                                  create_choice(
                                                      name="Oktober",   value=10),
                                                  create_choice(
                                                      name="November",  value=11),
                                                  create_choice(
                                                      name="Dezember",  value=12)
                                              ]
                                              )
                            ])
    async def listMonth(self, ctx: SlashContext, monat):
        cmdMonth = monat

        upcomming = SQL.execute(
            f"SELECT id, day, username, discriminator, nickname, show FROM birthdays WHERE month={cmdMonth}")
        # filter out all that disabled list parameter
        upcomming = list(filter(lambda x: x[-1] == 1, upcomming))
        self.bot.log.debug(f"found {upcomming}")

        if len(upcomming) == 0:
            listEmbed = Embed(
                title=f"Geburtstage im {months[cmdMonth-1][0]}",
                description=f"Es wurden keine Geburtstage im Monat {months[cmdMonth-1][0]} eingetragen oder als sichtbar markiert.",
                color=0xc59e25
            )
            listEmbed.set_footer(
                text=f"{self.bot.user.display_name} > Geburtstag", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=listEmbed, hidden=True)
            return

        has_unknown = False
        for i in range(len(upcomming)):
            id, day, username, discriminator, nickname, *_ = upcomming[i]
            member = self.bot.guild.get_member(id)
            if member:
                display_name = member.mention
            else:
                if nickname:
                    display_name = f"{nickname} ({username} #{int(discriminator):04}) *"
                else:
                    display_name = f"{username} #{int(discriminator):04} *"
                has_unknown = True
            upcomming[i] = (
                day, f"`{str(day).rjust(2)}.{str(cmdMonth).rjust(2)}.`: {display_name}")

        # sort by day, which is the first item in every tuple
        upcomming = sorted(upcomming, key=lambda d: d[0])
        upcomming = [x[1] for x in upcomming]  # make a list of tuples to list
        # join all lines together with newlines inbetween
        lines = '\n'.join(upcomming)

        listEmbed = Embed(
            title=f"Geburtstage im {months[cmdMonth-1][0]}",
            color=0x00ff00
        )
        listEmbed.add_field(
            name=f"{len(upcomming)} Geburtstag{'' if len(upcomming) == 1 else 'e'}", value=lines, inline=False)
        if has_unknown:
            listEmbed.add_field(
                name="Notiz", value="\* *Diese Person ist nicht mehr auf dem Server. Der angezeigte Name ist der letzte bekannte Name und dieser könnte sich inzwischen schon geändert haben.*")
        listEmbed.set_footer(
            text=f"{self.bot.user.display_name} > Geburtstag", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=listEmbed)

    async def checkBirthday(self):
        self.today = date.today()
        ids_list = []
        self.members = []

        self.bot.log.info(
            f"Checking for Birthdays...\ntoday is:\n - Day: {self.today.day}\n - Month: {self.today.month}")
        for id_tuple in SQL.execute(f"SELECT id FROM birthdays WHERE day = {self.today.day} AND month = {self.today.month}").fetchall():
            # select first id from every tuple in the list
            ids_list.append(id_tuple[0])
        self.bot.log.debug(f"IDs: {ids_list}")
        if not ids_list:
            return

        for id in ids_list:
            self.members.append(await self.bot.guild.fetch_member(id))
        for member in self.members:
            bday_msg_1 = None
            bday_msg_2 = None
            image_url = None

            if member.id == 436948016268574721:  # flatschii ._.
                bday_msg_1 = "Flatschi flatscht ins nächste Jahr!"
                bday_msg_2 = "<:Kuchenmoji_Flatschgesicht:912366726476353547>"
                image_url = "https://cake4everyone.de/._.png"
            elif member.id == 541297460866449408:  # schoggili
                bday_msg_1 = "Schoggili futtert sich ins nächste Jahrli!"
                with open(path.join(path.dirname(__file__), 'birthday/bday_msg_2.txt'), 'r') as f:
                    bday_msg_2 = random.choice(f.readlines())
                    arr = bday_msg_2.replace('.', '').replace('!', '').replace("Geburtstag", "Burzeltag").split(' ')
                    arr[0] = arr[0].lower()
                    random.shuffle(arr)
                    arr[0] = arr[0].capitalize()
                    bday_msg_2 = ' '.join(arr) + '.'
                image_url = "https://cake4everyone.de/keks.png"

            if bday_msg_1 == None:
                with open(path.join(path.dirname(__file__), 'birthday/bday_msg_1.txt'), 'r') as f:
                    bday_msg_1 = random.choice(
                        f.readlines()).format(name=member.mention)
            if bday_msg_2 == None:
                with open(path.join(path.dirname(__file__), 'birthday/bday_msg_2.txt'), 'r') as f:
                    bday_msg_2 = random.choice(f.readlines())
            if image_url == None:
                with urlopen(self.google_baseUrl.format(
                    count=1,
                    startIndex=random.randint(1, 200),
                    apiKey=self.google_apiKey,
                    searchEngine=self.google_searchEngine,
                    querry="birthday+cake"
                )) as f:
                    image_url = json.load(f)['items'][0]['link']

            birthdayEmbed = Embed(
                description=bday_msg_1 + '\n' + bday_msg_2,
                color=0x2f3136)
            birthdayEmbed.set_image(url=image_url)
            birthdayEmbed.set_footer(
                text=f"{self.bot.user.display_name} > Geburtstag", icon_url=self.bot.user.avatar_url)
            await self.bot.hauptchat.send(member.mention, delete_after=0.001)
            await self.bot.hauptchat.send(embed=birthdayEmbed)

    def nextDate(self, day, month):
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
        with open(path.join(path.dirname(path.dirname(__file__)), "lib/google_apiKey.0"), "r", encoding="utf-8") as f:
            self.google_apiKey = f.read()[:-1]
        with open(path.join(path.dirname(path.dirname(__file__)), "lib/google_searchEngine.0"), "r", encoding="utf-8") as f:
            self.google_searchEngine = f.read()[:-1]

        # misfire_grace_time=(16 hours, 59 minutes, 58 seconds) to run latest at 23:59:58 on that day
        self.bot.scheduler.add_job(self.checkBirthday, CronTrigger(
            hour=7), misfire_grace_time=61198)

        self.bot.cogs_ready.ready_up(path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(Birthday(bot))
