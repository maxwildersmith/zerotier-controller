from asyncio import sleep
import os
from os import getcwd
from pathlib import Path
import pickle
import git
import subprocess
import time
import discord
from discord.ext import commands


#initialize all bot commands
class cmds(commands.Cog, name="test"):
    def __init__(self, bot, controller):
        super().__init__()
        self.bot = bot
        self.ctrl = controller
        if not os.path.exists("./names.pickle"):
            print('creating dictionary')
            newDict= dict()
            with open("names.pickle", "wb") as file:
                pickle.dump(newDict, file, protocol=pickle.HIGHEST_PROTOCOL)
            
        with open("names.pickle", "rb") as file:
            self.names = pickle.load(file)

    @commands.command(name="ping")
    async def echo(self, ctx):

        await ctx.send(f"pong")

    @commands.command(name="auth")
    async def auth_member(self, ctx, *args):
        #attempt authorization
        if len(args) == 2:
            request = self.ctrl.auth_member(args[0])
            if request == "auth":
                await ctx.send(f"authorization successful, member {args[0]} is now in the network and assigned name {args[1]}")
                self.names[args[0]] = args[1]

                #dump to pickle file to save
                with open("names.pickle", "wb") as file:
                    pickle.dump(self.names, file, pickle.HIGHEST_PROTOCOL)

            elif request == "noauth":
                await ctx.send(f"authorization failed, please try again or contact admin")
            elif request == "nomem":
                await ctx.send(f"member not found, please join the network ({self.ctrl.get_nwid()}) before proceeding")
            elif request == "error":
                await ctx.send(f"your ID was found, but some other error occured, please contact a network administrator")
            
        else:
            await ctx.send(f"Expected 1 argument (member ID), but got {len(args)}, \nplease try again")
    
    @commands.command(name="memberlist")
    async def mem_list(self, ctx, *args):
        mems = self.ctrl.get_members()
        message = f"the following members are on the network: "
        for mem in mems:
            if mem in self.names.keys():
                message = message + f"{self.names[mem]}:{mem}, "
            else:
                message = message + f"NoName:{mem}, "
        
        await ctx.send(message)

    @commands.command(name="info")
    async def network_info(self, ctx, *args):
        networks = self.ctrl.network_info()
        printStr = "printing info for the controller networks..."
        for network in networks.keys():
            printStr += network + "\n"
            for info in networks[network].keys():
                printStr += f"\t\t{info} : {networks[network][info]}\n"
        await ctx.send(printStr)
    
    @commands.command(name="memberinfo")
    async def member_info(self, ctx, *args):
        if len(args) != 1:
            await ctx.send(f"incorrect number of command arguments, expected 1 but got {len(args)}")
        else:
            await ctx.send(self.ctrl.member_info(args[0]) + f"\t\tmemberName: {self.names[args[0]]}")

    #TODO: the following two commands need to be implemented
    @commands.command(name="rename")
    async def rename(self, ctx, *args):
        if len(args) != 2:
            await ctx.send(f"incorrect number of command arguments, expected 2 (memberID, newName) but got {len(args)}")
        else:
            mems = self.ctrl.get_members()
            if args[0] in mems:
                self.names[args[0]] = args[1]

                #dump to pickle file to save
                with open("names.pickle", "wb") as file:
                    pickle.dump(self.names, file, pickle.HIGHEST_PROTOCOL)

                await ctx.send(f"your ID has been found, your name has been set to {args[1]}")
            else:
                await ctx.send(f"I didn't find your member ID in the list of network members\nplease add yourself to the network first and try again")
    
    def restart(self):
        subprocess.Popen('nohup systemctl restart ztbot', shell=True)

    
    @commands.command(name="help")
    async def help(self, ctx, *args):
        message = "Hi, I'm here to help you join the broncospace lab network\nCommands:"
        
        #command help messages
        ping = "\t**$ping**\n\t\treturns 'pong' message if bot is up"
        auth = "\t**$auth [memberID] [memberName]**\n\t\tauthorize a new member who joined the network and maps their ID to a name"
        memberlist = "\t**$memberlist**\n\t\treturns the list of all memberIDs and memberNames on the network"
        info = "\t**$info**\n\t\treturns information about all available networks"
        memberinfo = "\t**$memberinfo [memberID]**\n\t\treturns information about the specified member on the network(s)"
        rename = "\t**$rename [memberID] [memberName]**\n\t\tSets the name of a member on the network to improve readability of memberlist"
        update = "\t**$update**\n\t\tPulls updates to this discord bot from github and sets restarts the bot with them"

        for cmd in [ping, auth, memberlist, info, memberinfo, rename, update]:
            message += (f"\n{cmd}")
        
        await ctx.send(message)
