import discord 
from base_bot import Bot
from constants import DISCORD_TOKEN

intents = discord.Intents.default()
# intents.message_contents = True

class DiscordBot(Bot):
    def __init__(self):
        super().__init__()
        self.client = discord.Client(intents=intents)
        print("Discord bot initialized")

    def run(self) -> None:
        """
        Run the discord bot
        """
        @self.client.event
        async def on_message(message):
            if message.author == self.client.user:
                return

            if message.content.startswith("!ping"):
                await message.channel.send("pong")

            elif message.content.startswith("!auth"):
                args = message.content.split(" ")
                if len(args) == 4:
                    request = self.auth_member(args[2], args[3])
                    if request == "auth":
                        await message.channel.send(f"authorization successful, member {args[4]} is now in the network and assigned name {args[3]}")
                    elif request == "noauth":
                        await message.channel.send(f"authorization failed, please try again or contact admin")
                    elif request == "nomem":
                        await message.channel.send(f"member not found, please join the network ({self.get_network_id()}) before proceeding")
                    elif request == "error":
                        await message.channel.send(f"your ID was found, but some other error occured, please contact a network administrator")
                else:
                    await message.channel.send(f"invalid number of arguments, please try again")
            elif message.content.startswith("!memberlist"):
                members = self.get_members()
                memberlist = ""
                for member in members:
                    memberlist += f"{member}: {members[member]}\n"
                await message.channel.send(memberlist)
            elif message.content.startswith("!networkinfo"):
                networks = self.get_network_info()
                printStr = "printing info for the controller networks..."
                for network in networks.keys():
                    printStr += network + "\n"
                    for info in networks[network].keys():
                        printStr += f"{info}: {networks[network][info]}\n"
                await message.channel.send(printStr)
            elif message.content.startswith("!memberinfo"):
                args = message.content.split(" ")
                if len(args) == 3:
                    info = self.get_member_info(args[2])
                    printStr = f"printing info for member {args[2]}...\n"
                    for key in info.keys():
                        printStr += f"{key}: {info[key]}\n"
                    await message.channel.send(printStr)
                else:
                    await message.channel.send(f"invalid number of arguments, please try again")
            elif message.content.startswith("!help"):
                await message.channel.send("Commands:\n!ping - ping the bot\n!auth <member ID> <name> - authorize a member to join the network\n!memberlist - list all members in the network\n!networkinfo - get info about the network\n!memberinfo <member ID> - get info about a member\n!help - display this message")


        self.client.run(DISCORD_TOKEN)