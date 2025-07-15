import json
import sys
import aiohttp
import websockets
import asyncio
import random

GATEWAY_URL = ""

API_VERSION = 10
BASE_URL = f"https://discord.com/api/v{API_VERSION}"
TOKEN = ""

GATEWAY_ENDPOINT = "/gateway"
SEQ_NUMBER = None
LAST_HEARTBEAT_ACK = True

SESSION = None


class Status():
    online = "online"
    dnd = "dnd"
    idle = "idle"
    invisible = "invisible"
    offline = "offline"


class OptionType():
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
    MENTIONABLE = 9
    NUMBER = 10
    ATTACHMENT = 11


class ChannelsType():
    UNHANDLED = -1
    DM = 1
    GROUP_DM = 3
    GUILD_TEXT = 0
    GUILD_VOICE = 2
    GUILD_CATEGORY = 4
    GUILD_ANNOUNCEMENT = 5
    GUILD_STORE = 6
    ANNOUNCEMENT_THREAD = 10
    PUBLIC_THREAD = 11
    PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13
    GUILD_DIRECTORY = 14
    GUILD_FORUM = 15


class Interaction():
    interaction_id = 0
    interaction_token = ""
    # TODO: abstract to User object
    user_id = 0

    def __init__(self, interaction_id, interaction_token, user_id):
        self.interaction_id = interaction_id
        self.interaction_token = interaction_token
        self.user_id = user_id

    async def respond(self, response):
        async with SESSION.post(
                BASE_URL +
            f"/interactions/{self.interaction_id}/{self.interaction_token}/callback",
				# TODO: different types of responses
                json={"type": 4, "data": {"content": response}},
                headers={"Authorization": f"Bot {TOKEN}"}
        ) as response:
            print(await response.text())


class Bot():
    __listeners = {}
    __command_map = []
    __commands = {}
    __options = {}
    status = None

    def __init__(self, status: Status = Status.online):
        self.status = status

    def run(self, token):
        global TOKEN

        TOKEN = token
        asyncio.run(main(self))

    def get_listeners(self):
        return self.__listeners

    def get_commands(self):
        return self.__commands

    def get_command_map(self):
        return self.__command_map

    def event(self, func):
        if asyncio.iscoroutinefunction(func):
            self.__listeners.setdefault(func.__name__.lower(), []).append(func)
        else:
            raise TypeError(
                f"Event handler '{func.__name__}' must be an async function")

        return func

    def command(self, description: str = ""):
        def decorator(func):
            self.__commands[func.__name__] = func

            self.__options[func.__name__].reverse()
            self.__command_map.append({
                "name": func.__name__,
                "type": 1,
                "description": description,
                "options": self.__options[func.__name__],
            })

            return func

        return decorator

    def option(self, name: str, description: str, option_type: OptionType, required: bool):
        def decorator(func):
            self.__options.setdefault(func.__name__, []).append({
                "name": name,
                "description": description,
                "type": option_type,
                "required": required,
            })

            return func

        return decorator


async def main(bot):
    global SEQ_NUMBER
    global LAST_HEARTBEAT_ACK

    global SESSION
    SESSION = aiohttp.ClientSession()
    async with SESSION.get(BASE_URL + GATEWAY_ENDPOINT) as response:
        response = await response.json()
        GATEWAY_URL = response["url"]

    async with websockets.connect(GATEWAY_URL) as websocket:
        async for message in websocket:
            data = json.loads(message)

            print(data["op"], data["t"], data)

            if data["op"] == 0:
                if data["t"] == "READY":
                    application_id = data["d"]["user"]["id"]
                    async with SESSION.put(
                            BASE_URL +
                        f"/applications/{application_id}/commands",
                            json=bot.get_command_map(),
                            headers={"Authorization": f"Bot {TOKEN}"}
                    ) as response:
                        # TODO: handle response code
                        print(await response.text())

                if data["t"] == "INTERACTION_CREATE":
                    commands = bot.get_commands()
                    # TODO: Match by id
                    command = commands.get(data["d"]["data"]["name"])
                    if command:
                        if data["d"]["channel"]["type"] == ChannelsType.DM:
                            user_id = int(data["d"]["user"]["id"])
                        else:
                            user_id = int(data["d"]["member"]["user"]["id"])

                        interaction = Interaction(
                                        data["d"]["id"], 
                                        data["d"]["token"],
                                        user_id
                                    )
                        asyncio.create_task(
                            command(interaction, *data["d"]["data"]["options"]))

                event_listeners = bot.get_listeners().get(
                    "on_" + data["t"].lower())
                if event_listeners:
                    for func in event_listeners:
                        asyncio.create_task(func())

            if data["op"] == 1:
                await websocket.send(json.dumps({
                    "op": 1,
                    "d": SEQ_NUMBER
                }))

            if data["op"] == 10:
                asyncio.create_task(heartbeat_loop(
                    websocket, data["d"]["heartbeat_interval"]))
                await websocket.send(json.dumps({
                    "op": 2,
                    "d": {
                        "token": TOKEN,
                        "intents": 53608447,
                        "properties": {
                            "os": sys.platform,
                            "browser": "Tuincord",
                            "device": "Tuincord",
                        },
                        "presence": {
                            # "since": 91879201,
                            # "activities": [{
                            #     "name": "Save the Oxford Comma",
                            #             "type": 0
                            # }],
                            "status": bot.status,
                        }
                        # TODO: "compress": True,
                    },
                }))

            if data["op"] == 11:
                LAST_HEARTBEAT_ACK = True

            if data.get("s") is not None:
                SEQ_NUMBER = data["s"]


async def heartbeat_loop(websocket, interval):
    while True:
        if not LAST_HEARTBEAT_ACK:
            # TODO: restore connection
            websocket.close()

        jitter = random.random()

        await asyncio.sleep(interval / 1000 * jitter)

        await websocket.send(json.dumps({
            "op": 1,
            "d": SEQ_NUMBER
        }))

if __name__ == "__main__":
    asyncio.run(main())
