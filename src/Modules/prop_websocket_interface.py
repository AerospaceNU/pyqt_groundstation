import time
from src.Modules.data_interface_core import ThreadedModuleCore
from src.constants import Constants
import websockets, asyncio, json


class PropWebsocketInterface(ThreadedModuleCore):

    def __init__(self):
        super().__init__()
        self.serial_devices["Prop Websocket"] = self.changeWsServer
        self.serial_port = ""
        self.nextCheckTime = time.time()
        self.loop = asyncio.new_event_loop()

        self.primary_module = True

    def changeWsServer(self, name):
        self.serial_port = f"ws://{name}:9002"

    def spin(self):
        self.loop.run_until_complete(self.mainLoop())

    def parseData(self, data):
        self.data_dictionary[Constants.raw_message_data_key] = {"Prop data": [[key, str(data["data"][key])] for key in data["data"]]}

    async def mainLoop(self):
        try:
            if self.serial_port == "":
                return
            async with websockets.connect(self.serial_port) as websocket:
                connected = True
                while connected:
                    try:
                        data_str = await websocket.recv()
                        parsed = json.loads(data_str)
                        print(parsed)

                        self.parseData(parsed)
                    except Exception as e:
                        connected = False
                        self.logToConsole("Lost connection to prop stand: {}".format(e), 2)

        except Exception as e:
            self.logToConsole("Couldn't connect to prop stand: {}".format(e), 2)

        if not self.should_be_running:
            self.loop.stop()
        else:
            time.sleep(1)
