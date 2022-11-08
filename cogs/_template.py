
from discord.ext.commands import Cog
import json
from os import path
# import sys
# sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
# # import ../files/sql.py
# from files import sql as SQL

with open(path.join(path.dirname(path.dirname(__file__)), "config.json")) as f:
    guild_id = json.load(f)['base']['guild_id']


class COGNAME(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        self.bot.cogs_ready.ready_up(path.basename(__file__)[:-3])

def setup(bot):
    bot.add_cog(COGNAME(bot))
