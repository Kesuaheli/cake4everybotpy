from os import path
import json
from discord_slash.utils.manage_commands import create_choice, create_option
from discord_slash import cog_ext, SlashContext
from discord import Embed
from discord.ext.commands import Cog, Bot
from datetime import datetime, timedelta
from files import sql as SQL


with open(path.join(path.dirname(path.dirname(__file__)), "config.json")) as f:
    guild_id = json.load(f)['base']['guild_id']


class Spielecke(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    # a slash command to create a discord guild event
    @cog_ext.cog_subcommand(base="spielecke", name="neu",
                            description="Create a game event",
                            guild_ids=[guild_id]
                            )
    async def spielecke(self, ctx: SlashContext):
        (
            await self.bot.get_guild(guild_id)
            .create_scheduled_event(name="new game", description="description", start_time=datetime.now()+timedelta(minutes=2))
        )

    @Cog.listener()
    async def on_ready(self):
        self.bot.cogs_ready.ready_up(path.basename(__file__)[:-3])


def setup(bot: Bot):
    bot.add_cog(Spielecke(bot))
