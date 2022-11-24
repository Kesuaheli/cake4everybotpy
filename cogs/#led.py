#import board
from rpi_ws281x import *
from time import sleep
from os import path
import sys
import random
import json
import re

import discord
from discord.ext.commands import Cog
from discord import Embed
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option

with open(path.join(path.dirname(path.dirname(__file__)), "config.json")) as f:
    test_guild = json.load(f)['guild']['test']

AMOUNT = 288
PIN = 18
FREQ = 800000
DMA = 10
INVERT = False
BRIGTHNESS = 255
CHANNEL = 0

COLORS = {
    'red':    Color(255,   0,   0),
    'green':  Color(0,   255,   0),
    'blue':   Color(0,     0, 255),
    'yellow': Color(255, 255,   0),
    'cyan':   Color(0,   255, 255),
    'purple': Color(255,   0, 255),
    'white':  Color(255, 255, 255)
}

strip = Adafruit_NeoPixel(AMOUNT, PIN, FREQ, DMA, INVERT, BRIGTHNESS, CHANNEL)
strip.begin()


def colorChoiceList():
    colorChoice = []
    for name, value in COLORS.items():
        colorChoice.append(create_choice(name=name, value=value))
    return colorChoice


class Led(Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_subcommand(base="led", subcommand_group="all", name="list",
                            base_description="LEDs strip configuration",
                            subcommand_group_description="Fill all LEDs in the strip with the same color.",
                            description="Fill all LEDs in the strip with the same color. Select from a list of predefined colors",
                            guild_ids=[test_guild],
                            options=[
                                create_option(name="color",
                                              description="select the color to fill the strip with",
                                              required=True,
                                              option_type=4,
                                              choices=colorChoiceList()
                                              ),
                                create_option(name="brightness",
                                              description="modify the brightness percentage of the hole strip.",
                                              required=False,
                                              option_type=4,
                                              min_value=0,
                                              max_value=100
                                              )
                            ]
                            )
    async def allList(self, ctx: SlashContext, color, brightness=None):
        Led.fill(0, AMOUNT, color, brightness)
        await ctx.send("WIP", hidden=True)

    @cog_ext.cog_subcommand(base="led", subcommand_group="all", name="rgb",
                            base_description="LEDs strip configuration",
                            subcommand_group_description="Fill all LEDs in the strip with the same color.",
                            description="Fill all LEDs in the strip with the same color. Type a custom RGB color.",
                            guild_ids=[test_guild],
                            options=[
                                create_option(name="r",
                                              description="Select the red value of your color to fill the strip with",
                                              required=True,
                                              option_type=4,
                                              min_value=0,
                                              max_value=255
                                              ),
                                create_option(name="g",
                                              description="Select the green value of your color to fill the strip with",
                                              required=True,
                                              option_type=4,
                                              min_value=0,
                                              max_value=255
                                              ),
                                create_option(name="b",
                                              description="Select the blue value of your color to fill the strip with",
                                              required=True,
                                              option_type=4,
                                              min_value=0,
                                              max_value=255
                                              ),
                                create_option(name="brightness",
                                              description="modify the brightness percentage of the hole strip.",
                                              required=False,
                                              option_type=4,
                                              min_value=0,
                                              max_value=100
                                              )
                            ]
                            )
    async def allRGB(self, ctx: SlashContext, r, g, b, brightness=None):
        Led.fill(0, AMOUNT, Color(r, g, b), brightness)
        await ctx.send("WIP", hidden=True)

    @cog_ext.cog_subcommand(base="led", subcommand_group="all", name="hex",
                            base_description="LEDs strip configuration",
                            subcommand_group_description="Fill all LEDs in the strip with the same color.",
                            description="Fill all LEDs in the strip with the same color. Type a custom HEX color.",
                            guild_ids=[test_guild],
                            options=[
                                create_option(name="hex",
                                              description="Select the red value of your color to fill the strip with",
                                              required=True,
                                              option_type=3
                                              ),
                                create_option(name="brightness",
                                              description="modify the brightness percentage of the hole strip.",
                                              required=False,
                                              option_type=4,
                                              min_value=0,
                                              max_value=100
                                              )
                            ]
                            )
    async def allHEX(self, ctx: SlashContext, hex, brightness=None):
        rgb = Led.hexToRGB(hex)
        if not rgb:
            await ctx.send("not a valid hex", hidden=True)
            return

        r, g, b = rgb
        Led.fill(0, AMOUNT, Color(r, g, b), brightness)
        await ctx.send("WIP", hidden=True)

    @cog_ext.cog_subcommand(base="led", subcommand_group="range", name="list",
                            base_description="LEDs strip configuration",
                            subcommand_group_description="Fill a range of LEDs in the strip with the same color.",
                            description="Fill a range of LEDs in the strip with the same color. Select from a list of predefined colors",
                            guild_ids=[test_guild],
                            options=[
                                create_option(name="start",
                                              description="Select the startpoint of the range.",
                                              required=True,
                                              option_type=4,
                                              min_value=1,
                                              max_value=AMOUNT-1
                                              ),
                                create_option(name="to",
                                              description="Select the endpoint of the range.",
                                              required=True,
                                              option_type=4,
                                              min_value=1,
                                              max_value=AMOUNT-1
                                              ),
                                create_option(name="color",
                                              description="Select the color to fill the strip with.",
                                              required=True,
                                              option_type=4,
                                              choices=colorChoiceList()
                                              ),
                                create_option(name="brightness",
                                              description="Modify the brightness percentage of the hole strip.",
                                              required=False,
                                              option_type=4,
                                              min_value=0,
                                              max_value=100
                                              )
                            ]
                            )
    async def rangeList(self, ctx: SlashContext, start, to, color, brightness=None):
        Led.fill(min(start, to)-1, max(start, to), color, brightness)
        await ctx.send("WIP", hidden=True)

    @cog_ext.cog_subcommand(base="led", subcommand_group="range", name="rgb",
                            base_description="LEDs strip configuration",
                            subcommand_group_description="Fill a range of LEDs in the strip with the same color.",
                            description="Fill a range of LEDs in the strip with the same color. Type a custom RGB color.",
                            guild_ids=[test_guild],
                            options=[
                                create_option(name="start",
                                              description="Select the startpoint of the range.",
                                              required=True,
                                              option_type=4,
                                              min_value=1,
                                              max_value=AMOUNT-1
                                              ),
                                create_option(name="to",
                                              description="Select the endpoint of the range.",
                                              required=True,
                                              option_type=4,
                                              min_value=1,
                                              max_value=AMOUNT-1
                                              ),
                                create_option(name="r",
                                              description="Select the red value of your color to fill the strip with",
                                              required=True,
                                              option_type=4,
                                              min_value=0,
                                              max_value=255
                                              ),
                                create_option(name="g",
                                              description="Select the green value of your color to fill the strip with",
                                              required=True,
                                              option_type=4,
                                              min_value=0,
                                              max_value=255
                                              ),
                                create_option(name="b",
                                              description="Select the blue value of your color to fill the strip with",
                                              required=True,
                                              option_type=4,
                                              min_value=0,
                                              max_value=255
                                              ),
                                create_option(name="brightness",
                                              description="modify the brightness percentage of the hole strip.",
                                              required=False,
                                              option_type=4,
                                              min_value=0,
                                              max_value=100
                                              )
                            ]
                            )
    async def rangeRGB(self, ctx: SlashContext, start, to, r, g, b, brightness=None):
        Led.fill(min(start, to)-1, max(start, to), Color(r, g, b), brightness)
        await ctx.send("WIP", hidden=True)

    @cog_ext.cog_subcommand(base="led", subcommand_group="range", name="hex",
                            base_description="LEDs strip configuration",
                            subcommand_group_description="Fill a range of LEDs in the strip with the same color.",
                            description="Fill a range of LEDs in the strip with the same color. Type a custom HEX color.",
                            guild_ids=[test_guild],
                            options=[
                                create_option(name="start",
                                              description="Select the startpoint of the range.",
                                              required=True,
                                              option_type=4,
                                              min_value=1,
                                              max_value=AMOUNT-1
                                              ),
                                create_option(name="to",
                                              description="Select the endpoint of the range.",
                                              required=True,
                                              option_type=4,
                                              min_value=1,
                                              max_value=AMOUNT-1
                                              ),
                                create_option(name="hex",
                                              description="Select the red value of your color to fill the strip with",
                                              required=True,
                                              option_type=3
                                              ),
                                create_option(name="brightness",
                                              description="modify the brightness percentage of the hole strip.",
                                              required=False,
                                              option_type=4,
                                              min_value=0,
                                              max_value=100
                                              )
                            ]
                            )
    async def rangeHEX(self, ctx: SlashContext, start, to, hex, brightness=None):
        rgb = Led.hexToRGB(hex)
        if not rgb:
            await ctx.send("not a valid hex", hidden=True)
            return

        r, g, b = rgb
        Led.fill(min(start, to)-1, max(start, to), Color(r, g, b), brightness)
        await ctx.send("WIP", hidden=True)

    @cog_ext.cog_subcommand(base="led", name="brightness",
                            base_description="LEDs strip configuration",
                            description="Modify the brightness percentage of the hole strip.",
                            guild_ids=[test_guild],
                            options=[
                                create_option(name="brightness",
                                              description="Enter the number of the new brightness in percent.",
                                              required=True,
                                              option_type=4,
                                              min_value=0,
                                              max_value=100
                                              )
                            ]
                            )
    async def setBrightness(self, ctx: SlashContext, brightness):
        strip.setBrightness(int(brightness*2.55))
        strip.show()
        await ctx.send("WIP", hidden=True)

    @cog_ext.cog_subcommand(base="led", name="clear",
                            base_description="LEDs strip configuration",
                            description="Simply clear all LEDs in the strip.",
                            guild_ids=[test_guild]
                            )
    async def clear(self, ctx: SlashContext):
        Led.fill(0, AMOUNT, 0)
        await ctx.send("WIP", hidden=True)

    @Cog.listener()
    async def on_ready(self):
        self.bot.cogs_ready.ready_up(path.basename(__file__)[:-3])

    @staticmethod
    def hexToRGB(hex):
        if not len(hex) >= 4:
            return None
        if hex.startswith('#'):
            hex = hex[1:]
        elif hex.startswith('0x'):
            hex = hex[2:]

        if not len(hex) == 6 or len(hex) == 3:
            return None
        pattern = r"^[A-Fa-f0-9]{6}|[A-Fa-f0-9]{3}$"
        if not re.match(pattern, hex):
            return None

        r = hex[:-4] if len(hex) == 6 else hex[:-2]*2
        g = hex[2:-2] if len(hex) == 6 else hex[1:-1]*2
        b = hex[4:] if len(hex) == 6 else hex[2:]*2

        r = int(r, base=16)
        g = int(g, base=16)
        b = int(b, base=16)
        return r, g, b

    @staticmethod
    def fill(start, end, color, brightness=None):
        if brightness == 0:
            color = 0
        for i in range(start, end):
            strip.setPixelColor(i, color)
        if brightness:
            strip.setBrightness(int(brightness*2.55))
        strip.show()


def setup(bot):
    if bot.debug:
        return  # led module not loaded in debug mode
    bot.add_cog(Led(bot))
