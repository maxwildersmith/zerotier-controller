import slack
from base_bot import Bot, names, names_lock
from constants import *
from flask import Flask, request
from slackeventsapi import SlackEventAdapter

app = Flask(__name__)
event_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events", app)


class SlackBot(Bot):
    def __init__(self, channel_name: str):
        super().__init__()

        self.client = slack.WebClient(token=SLACK_TOKEN)

        self.channel_name = channel_name
        conversation = self.client.conversations_list()
        for channel in conversation["channels"]:
            if channel["name"] == self.channel_name:
                self.channel_id = channel["id"]

        self.client.chat_postMessage(channel=self.channel_name, text="Hello World! ZT Bot is online!")
        print("Slack bot initialized")

    def run(self) -> None:
        """
        Run the slack bot
        """
        # when pinged only
        @event_adapter.on("app_mention")
        def handle_message(event_data):
            self.message(event_data)

        app.run(debug=False)

        
    def message(self, event_data):
        """
        Handles messages sent to the slack channel
        """
        print(event_data)
        message = event_data["event"]
        if message.get("channel") == self.channel_id:
            text = message.get("text")
            if "ping" in text:
                self.client.chat_postMessage(channel=self.channel_name, text="pong")
            elif "auth" in text:
                args = message.get("text").split(" ")
                if len(args) == 4:
                    request = self.auth_member(args[2], args[3])
                    if request == "auth":
                        self.client.chat_postMessage(channel=self.channel_name, text=f"authorization successful, member {args[4]} is now in the network and assigned name {args[3]}")
                    elif request == "noauth":
                        self.client.chat_postMessage(channel=self.channel_name, text=f"authorization failed, please try again or contact admin")
                    elif request == "nomem":
                        self.client.chat_postMessage(channel=self.channel_name, text=f"member not found, please join the network ({self.get_network_id()}) before proceeding")
                    elif request == "error":
                        self.client.chat_postMessage(channel=self.channel_name, text=f"your ID was found, but some other error occured, please contact a network administrator")
                else:
                    self.client.chat_postMessage(channel=self.channel_name, text=f"Expected 2 arguments (member ID and name), but got {len(args) - 1}, \nplease try again")
            elif "memberlist" in text:
                mems = self.get_members()
                message = f"the following members are on the network: "
                for mem in mems:
                    message = message + f"{mems[mem]}: {mem}, "
                self.client.chat_postMessage(channel=self.channel_name, text=message)
            elif "networkinfo" in text:
                networks = self.get_network_info()
                printStr = "printing info for the controller networks..."
                for network in networks.keys():
                    printStr += network + "\n"
                    for info in networks[network].keys():
                        printStr += f"{info}: {networks[network][info]}\n"
                self.client.chat_postMessage(channel=self.channel_name, text=printStr)
            elif "memberinfo" in text:
                args = message.get("text").split(" ")
                if len(args) == 3:
                    info = self.get_member_info(args[2])
                    self.client.chat_postMessage(channel=self.channel_name, text=f"Member {args[2]} info:\n{info}")
                else:
                    self.client.chat_postMessage(channel=self.channel_name, text=f"Expected 1 argument (member ID), but got {len(args) - 1}, \nplease try again")
            elif message.get("text") == "help":
                self.client.chat_postMessage(channel=self.channel_name, text=f"ZT Bot Help:\n\nping - pong\nauth <member ID> <name> - authorize member with given ID and assign them the given name\nmemberlist - list all members on the network\nnetworkinfo - print info about the network\nmemberinfo <member ID> - print info about member with given ID\nhelp - print this message")

            

    