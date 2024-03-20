import requests
import json
from constants import CONTROLLER_TOKEN, NODEID, NWID
from threading import Lock
import pickle
import os

# shared dict for storing names
names = None
names_lock = Lock()
names_file = __file__.replace("base_bot.py", "names.pickle")

class Bot():
    def __init__(self):
        """
        Wraps the zerotier controller API for use in a base bot
        """
        global names

        # Check that we have the required API keys
        if CONTROLLER_TOKEN == "YOUR TOKEN HERE" or NODEID == "YOUR NODE ID HERE" or NWID == "YOUR NETWORK ID HERE":
            raise ValueError("Please replace the placeholder API keys in constants.py with your own")

        self.token = CONTROLLER_TOKEN
        self.nwid = NWID
        self.nodeid = NODEID


        with names_lock:
            if names is None:
                print("Names not initialized, initializing...")
                if os.path.exists(names_file):
                    print("loading names from pickle file")
                    with open(names_file, "rb") as file:
                        names = pickle.load(file)
                else:
                    print("creating new names dict")
                    names = dict()

        self.headers = {"X-ZT1-AUTH": self.token, "Content-Type": "application/json"}
        print("Base bot initialized")

    def run(self) -> None:
        """
        Abstract method for running the bot
        """
        raise NotImplementedError

    def quit(self) -> None:
        """
        Abstract method for quitting the bot
        """
        raise NotImplementedError

    def auth_member(self, UID: str, name: str = "UNKNOWN") -> str:
        """
        UID: str - the UID of the member to authorize
        name: str - the name to assign to the member, defaults to "UNKNOWN"
        Authorize member based on their node id (displayed in ZT windows widget or in CLI)
        """
        auth_post = None
        message = ""
        try:
            members = self.get_members()
            if UID in members.keys():
                auth_post = requests.post(f'http://localhost:9993/controller/network/{self.nwid}/member/{UID}', headers=self.headers, data=json.dumps({"authorized": True}))
                auth_get = requests.get(f'http://localhost:9993/controller/network/{self.nwid}/member/{UID}', headers=self.headers).json()
                if (auth_get["authorized"]):
                    message = "auth"
                    with names_lock:
                        names[UID] = name
                        with open("names.pickle", "wb") as file:
                            pickle.dump(names, file, pickle.HIGHEST_PROTOCOL)
                else:
                    message = "noauth"
            else:
                message = "nomem"
        except Exception as e:
            message = f"ERR: {e}"
        
        return message

    def get_members(self):
        """
        Returns a dictionary of members in the network, with their UID as the key
        """
        members = requests.get(f'http://localhost:9993/controller/network/{self.nwid}/member/', headers=self.headers).json()
        # look up names for each member
        res = dict()
        with names_lock:
            for member in members.keys():
                if member in names.keys():
                    res[member] = names[member]
        
        return res

    def get_network_id(self) -> str:
        """
        Returns the network id of the controller
        """
        return self.nwid

    def get_network_info(self) -> dict:
        """
        Returns a dictionary of the network info
        """
        networks = requests.get(f"http://localhost:9993/controller/network", headers=self.headers).json()

        net_info = dict()
        for network in networks:
            info = requests.get(f"http://localhost:9993/controller/network/{network}", headers=self.headers).json()
            net_info[network] = info
        return net_info

    def get_member_info(self, member: str) -> str:
        """
        Returns a string with the member info of the member with the given UID
        """
        networks = requests.get(f"http://localhost:9993/controller/network", headers=self.headers).json()
        message = ""

        for network in networks:
            message += network + "\n"
            members = requests.get(f"http://localhost:9993/controller/network/{network}/member", headers=self.headers).json()
            if member in members.keys():
                message += "\t" + member + "\n"
                with names_lock:
                    if member in names.keys():
                        message += "\t\tname: " + names[member] + "\n"
                    else:
                        message += "\t\tname: UNKNOWN\n"
                mem_info = requests.get(f"http://localhost:9993/controller/network/{network}/member/{member}", headers=self.headers).json()
                for key in mem_info.keys():
                    message += "\t\t" + key + ": " + str(mem_info[key]) + "\n"
            else:
                message += "\t" + member + " not found\n"

        return message

