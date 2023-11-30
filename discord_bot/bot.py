import discord 
from base_bot import Bot

# intents = discord.Intents.default()
# intents.message_contents = True

class DiscordBot(Bot):
    def __init__(self):
        super().__init__()
        self.client = discord.Client(intents=intents)
        self.channel = None