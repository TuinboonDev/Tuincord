import json
import sys
import aiohttp
import websockets
import asyncio
import random

GATEWAY_URL = ""

API_VERSION = 10
BASE_URL = f"https://discord.com/api/v{API_VERSION}"

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

class Bot():
    __listeners = {}
    __commands = {}
    __token = ""
    status = None

    def __init__(self, status=Status.online):
        self.status = status

    def run(self, token):
        self.__token = token
        asyncio.run(main(self))

    def get_token(self):
        return self.__token

    def get_listeners(self):
        return self.__listeners

    def event(self, func):
        if asyncio.iscoroutinefunction(func):
            self.__listeners.setdefault(func.__name__.lower(), []).append(func)
        else:
            raise TypeError(
                f"Event handler '{func.__name__}' must be an async function")

        return func

    def command(self):
        def decorator(func):
            self.__commands[func.__name__.lower()] = func
            return func

        return decorator

    def option(self):
        def decorator(func):

            return func

        return decorator

    def get_commands(self):
        return self.__commands


async def main(bot):
    global SEQ_NUMBER
    global LAST_HEARTBEAT_ACK

    async with aiohttp.ClientSession() as session:
        global SESSION
        SESSION = session
        async with session.get(BASE_URL + GATEWAY_ENDPOINT) as response:
            response = await response.json()
            GATEWAY_URL = response["url"]

    async with websockets.connect(GATEWAY_URL) as websocket:
        async for message in websocket:
            data = json.loads(message)

            print(data["op"], data["t"], data)

            if data["op"] == 0:
                event_listeners = bot.get_listeners().get(data["t"].lower())
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
                        "token": bot.get_token(),
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
                print(SEQ_NUMBER)


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

        print(SEQ_NUMBER)

if __name__ == "__main__":
    asyncio.run(main())
