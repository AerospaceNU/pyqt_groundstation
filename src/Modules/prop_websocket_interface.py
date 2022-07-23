import logging
import time

import asyncio
import json
import websockets

from src.Modules.data_interface_core import ThreadedModuleCore
from src.Modules.DataInterfaceTools.annunciator_helper import AnnunciatorHelper
from src.constants import Constants

from src.CustomLogging.prop_logger import PropLogger

class PropWebsocketInterface(ThreadedModuleCore):

    def __init__(self):
        super().__init__()
        self.serial_devices["Prop Websocket"] = self.changeWsServer
        self.serial_port = ""
        self.nextCheckTime = time.time()
        self.loop = asyncio.new_event_loop()
        
        self.serial_logger = PropLogger()

        self.annunciator = AnnunciatorHelper()

        self.callbacks_to_add.append([Constants.prop_command_key, self.propCommandCallback])

        self.connected = False
        self.command_queue = []

        self.primary_module = True

    def propCommandCallback(self, command):
        if self.connected:
            self.command_queue.append(command)
        else:
            self.logger.error("Not connected to test stand, can't send command")

    def changeWsServer(self, name):
        self.serial_port = f"ws://{name}:9002"
        self.connected = False

    def spin(self):
        self.loop.run_until_complete(self.mainLoop())

    def parseData(self, data):
        # Log every message
        self.serial_logger.log_ws_msg(data)

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

                self.logger.info("Test stand state transition: {0} -> {1}".format(old_state, new_state))
            else:
                self.logger.warning("Unrecognized command message from stand: {}".format(data))
        else:
            self.logger.warning("Unrecognized message from stand: {}".format(data))
            return

    async def mainLoop(self):
        try:
            if self.serial_port == "":
                return

            self.logger.info("Attempting to connect to prop stand at {}".format(self.serial_port))
            async with websockets.connect(self.serial_port) as websocket:
                self.connected = True
                self.logger.info("Got connection to prop stand at {}".format(self.serial_port))

                while self.connected:
                    try:
                        data_str = await websocket.recv()
                        parsed = json.loads(data_str)

                        self.parseData(parsed)

                        self.logToConsoleThrottle("Still getting data from prop test stand", logging.DEBUG, 5)

                        if len(self.command_queue) > 0:
                            data_to_send = self.command_queue.pop(0)
                            self.logger.warning("Sending command to test stand:\n{}".format(data_to_send))
                            await websocket.send(data_to_send)

                        if not self.should_be_running:
                            self.connected = False
                    except Exception as e:
                        self.connected = False
                        self.logger.error("Lost connection to prop stand: {}".format(e))

                    self.updateAnnunciator()

        except Exception as e:
            self.logger.error("Couldn't connect to prop stand: {}".format(e))

        self.updateAnnunciator()

        if not self.should_be_running:
            self.loop.stop()
        else:
            time.sleep(1)

    def updateAnnunciator(self):
        if self.connected:
            self.annunciator.setAnnunciator(0, "Test Stand Connection", 0, "Connected to test stand at {}".format(self.serial_port))
        else:
            self.annunciator.setAnnunciator(0, "Test Stand Connection", 2, "No connection to test stand at {}".format(self.serial_port))

        self.data_dictionary[Constants.primary_annunciator] = self.annunciator.getList()
