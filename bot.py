import logging
from systemd.journal import JournaldLogHandler, Priority
import os, json
from os import path
from glob import glob
from asyncio import sleep

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from discord import Intents
from discord.ext.commands import Bot as BotBase
from discord_slash import SlashCommand

class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        LOG.info(f" - {cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])

class Bot(BotBase):
    def __init__(self):
        with open(path.join(os.path.dirname(__file__), "config.json")) as f:
            config_base = json.load(f)['base']

        self.debug = config_base['debug']
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        self.scheduler = AsyncIOScheduler()
        self.log = LOG

        intents = Intents.default()
        intents.members = True
        super().__init__(command_prefix="c4e!", self_bot=True, intents=intents, owner_ids=config_base['owner_ids'])
        self.slash = SlashCommand(self, sync_commands=True)

    def setup(self):
        for cog in COGS:
            if not cog.startswith('#') and not cog.startswith('_'):
                self.log.debug(f"loading extension in /cogs/{cog}...")
                self.load_extension(f"cogs.{cog}")

    def run(self):
        LOG.debug("running setup...")
        self.setup()

        with open(path.join(path.dirname(__file__), "lib/token.0"), "r", encoding="utf-8") as f:
            self.TOKEN = f.read()

        self.log.debug("running bot...")
        super().run(self.TOKEN, reconnect=True)
    async def on_connect(self):
        self.log.debug("bot connected")
    async def on_disconnect(self):
        pass
        #self.log.warning("bot disconnected")

    async def on_ready(self):
        if not self.ready:
            with open(path.join(os.path.dirname(__file__), "config.json")) as f:
                config = json.load(f)
            self.guild = self.get_guild(config['base']['guild_id'])
            self.hauptchat = self.get_channel(config['base']['msg_channel_id'])
            self.testGuild = self.get_guild(910968992695468132)
            self.stdout = self.get_channel(910968992695468135)
            self.yt_notify = self.get_channel(config['text_channel']['yt_notify'])
            self.scheduler.start()

            self.ready = True
            self.log.info("bot ready")
            await self.stdout.send("Hello")

        else:
            self.log.info("bot reconnected")

    async def on_message(self, msg):
        pass
        #self.log.debug("bot message received")


if __name__ == '__main__':
    with open(path.join(path.dirname(__file__), "config.json")) as f:
        debug = json.load(f)['base']['debug']

    if debug is not path.basename(path.dirname(path.dirname(__file__))).startswith("test"): # rewrite config file
        debug = not debug
        if debug:
            config = {
                "base": {
                    "debug": True,
                    "guild_id": 910968992695468132,
                    "msg_channel_id": 910968992695468135,
                    "owner_ids": [361172911886827521]
                },
                "voice_channel": {

                },
                "text_channel": {
                    "no_mic": 955506588930687066,
                    "yt_notify": 910968992695468135
                },
                "guild": {
                    "test": 910968992695468132,
                    "c4e": 906168159139160085
                }
            }
        else:
            config = {
                "base": {
                    "debug": False,
                    "guild_id": 906168159139160085,
                    "msg_channel_id": 906168159139160088,
                    "owner_ids": [361172911886827521]
                },
                "voice_channel": {

                },
                "text_channel": {
                    "no_mic": 912006597532864592,
                    "yt_notify": 1007028983264722964
                },
                "guild": {
                    "test": 910968992695468132,
                    "c4e": 906168159139160085
                }
            }
        with open(path.join(path.dirname(__file__), "config.json"), 'w') as f:
            json.dump(config, f, indent=4)

    if debug:
        #logger
        LOG = logging.getLogger('testbot')
        LOG.addHandler(JournaldLogHandler())
        LOG.setLevel(logging.DEBUG)
        #LOG.debug("text in dark gray")
        #LOG.info("text in white")
        #LOG.warning("text in bold white")
        #LOG.error("text in red")
    else:
        #logger
        LOG = logging.getLogger('cake4everybot')
        LOG.addHandler(JournaldLogHandler())
        LOG.setLevel(logging.INFO)
        #LOG.info("text in white")
        #LOG.warning("text in bold white")
        #LOG.error("text in red")

    COGS = [path.split("/")[-1][:-3] for path in glob(path.dirname(__file__) + '/cogs/*.py')]

    bot = Bot()
    bot.run()
