import time

import asyncio
import json
import websockets

from src.Modules.data_interface_core import ThreadedModuleCore
from src.constants import Constants


class PropWebsocketInterface(ThreadedModuleCore):

    def __init__(self):
        super().__init__()
        self.serial_devices["Prop Websocket"] = self.changeWsServer
        self.serial_port = ""
        self.nextCheckTime = time.time()
        self.loop = asyncio.new_event_loop()

        self.callbacks_to_add.append([Constants.prop_command_key, self.propCommandCallback])

        self.connected = False
        self.command_queue = []

        self.primary_module = True

    def propCommandCallback(self, command):
        if self.connected:
            self.command_queue.append(command)
        else:
            self.logToConsole("Not connected to test stand, can't send command", 2, override_disabled_check=True)

    def changeWsServer(self, name):
        self.serial_port = f"ws://{name}:9002"
        self.connected = False

    def spin(self):
        self.loop.run_until_complete(self.mainLoop())

    def parseData(self, data):
        if 'data' in data:
            sensor_data = data['data']

            drop_down_data = {}

            sensor_types = list(sensor_data.keys())
            for sensor_type in sensor_types:
                sensor_names = list(sensor_data[sensor_type].keys())
                drop_down_data[sensor_type] = []

                for sensor_name in sensor_names:
                    sensor_values = sensor_data[sensor_type][sensor_name]

                    if "sensorReading" in sensor_values:
                        sensor_reading = sensor_values["sensorReading"]
                    elif "valveState" in sensor_values:
                        sensor_reading = sensor_values["valveState"]
                    else:
                        sensor_reading = "NO DATA"

                    sensor_key = sensor_name
                    self.data_dictionary[sensor_key] = sensor_reading
                    drop_down_data[sensor_type].append([sensor_key, sensor_reading])

            self.data_dictionary[Constants.raw_message_data_key] = drop_down_data.copy()
        elif 'command' in data:
            command = data['command']

            if command == 'STATE_TRANSITION':
                transition_data = data['transition']

                new_state = transition_data['newState']
                old_state = transition_data['oldState']

                self.logToConsole("Test stand state transition: {0} -> {1}".format(old_state, new_state), 1)
            else:
                self.logToConsole("Unrecognized command message from stand: {}".format(data), 1)
        else:
            self.logToConsole("Unrecognized message from stand: {}".format(data), 1)
            return

    async def mainLoop(self):
        try:
            if self.serial_port == "":
                return

            self.logToConsole("Attempting to connect to prop stand at {}".format(self.serial_port), 1)
            async with websockets.connect(self.serial_port) as websocket:
                self.connected = True
                self.logToConsole("Got connection to prop stand at {}".format(self.serial_port), 1)

                while self.connected:
                    try:
                        data_str = await websocket.recv()
                        parsed = json.loads(data_str)

                        self.parseData(parsed)

                        self.logToConsoleThrottle("Still getting data from prop test stand", 0, 5)

                        if len(self.command_queue) > 0:
                            data_to_send = self.command_queue.pop(0)
                            self.logToConsole("Sending command to test stand:\n{}".format(data_to_send), 1)
                            await websocket.send(data_to_send)

                        if not self.should_be_running:
                            self.connected = False
                    except Exception as e:
                        self.connected = False
                        self.logToConsole("Lost connection to prop stand: {}".format(e), 2)

        except Exception as e:
            self.logToConsole("Couldn't connect to prop stand: {}".format(e), 2)

        if not self.should_be_running:
            self.loop.stop()
        else:
            time.sleep(1)
