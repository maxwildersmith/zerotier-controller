import os

import discord
from discord.ext import commands

from cogs import cmds

class ZTBot(commands.Bot):
    def __init__(self, command_prefix, controller):
        super().__init__(command_prefix=command_prefix, intents=discord.Intents.all())
        self.ctrl = controller
        self.remove_command('help')

    async def on_ready(self):
        await self.add_cog(cmds(self, controller=self.ctrl))
        print(f"Logged in as {self.user}")