from discBot import ZTBot
from constants import *
import os
import threading
from discord_bot.bot import DiscordBot
from slack_bot.bot import SlackBot


# Check if discord bot is enabled

if DISCORD_TOKEN != "":
    discord = DiscordBot()
    discord_thread = threading.Thread(target=discord.run)
    discord_thread.start()

# Check if slack bot is enabled
if SLACK_TOKEN != "":
    slack = SlackBot("general")
    slack_thread = threading.Thread(target=slack.run)
    slack_thread.start()