
from discord.ext.commands import Cog
import json
from os import path
# import sys
# sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
# # import ../files/sql.py
# from files import sql as SQL


class NoMIC(Cog):
    def __init__(self, bot):
        self.bot = bot


    @Cog.listener()
    async def on_voice_state_update(self, member, oldState, newState):
        with open(path.join(path.dirname(path.dirname(__file__)), "config.json")) as f:
            config = json.load(f)

        if member.guild.id == config['base']['guild_id']:
            no_mic = self.bot.get_channel(config['text_channel']['no_mic'])
            if (oldState.channel == None or oldState.afk) and not newState.channel == None and not newState.afk:
                self.bot.log.debug(f"{member.display_name} joined a channel")
                await no_mic.set_permissions(member, view_channel=True)
            elif not oldState.channel == None and not oldState.afk and (newState.channel == None or newState.afk):
                self.bot.log.debug(f"{member.display_name} left a channel")
                await no_mic.set_permissions(member, overwrite=None)

    @Cog.listener()
    async def on_ready(self):
        self.bot.cogs_ready.ready_up(path.basename(__file__)[:-3])

def setup(bot):
    bot.add_cog(NoMIC(bot))
