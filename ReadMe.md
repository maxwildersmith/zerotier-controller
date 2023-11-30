# ZeroTier Controller

## **Description**
This code is used to deploy a discord bot as interface for a single-network zerotier controller.

## **Controller Setup**

The basics of deploying a zerotier controller can be implemented by following [zerotier's controller guide](https://docs.zerotier.com/self-hosting/network-controllers/). In addition to this, there are a few other useful API calls for managing the network

To change the IP of an existing network member:
```console
$ curl -X POST "http://localhost:9993/controller/network/${NWID}/member/${MEMID}" -H "X-ZT1-AUTH: ${TOKEN}" -d '{ "ipAssignments": ["123.456.78.90"]}'
```

To delete a network:

```console
$ curl -X DELETE "http://localhost:9993/controller/network/${NWID}" -H "X-ZT1-AUTH: ${TOKEN}" -d '{"authorized": false}'
```

More information about the API can be found in [ZeroTier's API documentation](https://docs.zerotier.com/central/v1/)

## **Bot Deployment**
To create a functioning bot, we must first create the application through discord's developer portal. An in-depth guide on creating the bot application can be found [here](https://realpython.com/how-to-make-a-discord-bot-python/). Make sure to save the bot's token, as we'll need it to link the application to our code. In addition to this, we will also need the **controller token, Node ID, and Network ID from the controller setup**. These identifiers, along with the the discord application token must be placed in a .env file with the following format:
```python
# .env
DISCORD_TOKEN=
CONTROLLER_TOKEN=
NODEID=
NWID=
```

To ensure decent system uptime, it's a good idea to run the bot as a service. An example of a service file you might use can be found in [ztbot.service](ztbot.service). This service file should be modified to reflect the correct directory and environment name.

This service can be placed in the appropriate folder for services.
On jetson nano: 
```console
$ sudo mv ztbot.service /etc/systemd/system
```

and then run:
```console
$ sudo systemctl daemon-reload
$ sudo systemctl start ztbot
```

To ensure good uptime, it's a good idea to make this service run on boot:
```console
$ sudo systemctl enable ztbot
```

To allow this bot to be updated with with the $update command, give ownership of the repository over to root (or whatever user you selected in the service file):
```console
$ sudo chown root zerotier-controller
```
The discord bot should now be running, and should also start automatically on a system restart.
## **Usage**
The discord bot currently supports the following list of commands
* **$ping** - returns 'pong' message if bot is up
* **$auth [member id]** - authorize a new member who joined the network
* **$memberlist** - returns the list of all member IDs on the network
* **$info** - returns information about all available networks
* **$memberinfo {memberID}** - returns information about the specified member on the network

## **Support Notes**
* This python code is tested and working on python 3.8.0

* Running on python 3.6.9 caused compatibility errors between asyncio and discord.py
