import time
from src.Modules.data_interface_core import ThreadedModuleCore
import websockets, asyncio, json

class PropWebsocketInterface(ThreadedModuleCore):
    
    def __init__(self):
        super().__init__()
        self.serial_devices["Prop Websocket"] = self.changeWsServer
        self.serial_port = ""
        self.nextCheckTime = time.time()
        self.loop = asyncio.new_event_loop()
        
    def changeWsServer(self, name):
        self.serial_port = f"ws://{name}:9002"
        self.connected = False

    def spin(self):
        if self.nextCheckTime <= time.time():
            self.logToConsole("Trying to connect to ground station on {}".format(self.serial_port), 0)
            try:
                self.loop.run_until_complete(self.connectedLoop())
                self.nextCheckTime = time.time() + 1
            except IOError:
                self.logToConsole(
                    "Could not connect to ground station on port {}".format(self.serial_port),
                    2,
                )
                self.nextCheckTime = time.time() + 5

        self.connected = False
        self.has_data = False
        self.good_fcb_data = False


    async def connectedLoop(self):
        try:
            if self.serial_port == "":
                return
            async with websockets.connect(self.serial_port) as websocket: 
                while True:
                    data_str = await websocket.recv()
                    parsed = json.loads(data_str)
                    print(parsed)
        except Exception as e:
            print(e)