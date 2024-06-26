import os
import time
from os import listdir
from os.path import isfile, join
from typing import Dict, List

import pandas as pd

from src.constants import Constants
from src.data_helpers import quaternion_to_euler_angle
from src.Modules.DataInterfaceTools.comms_console_helper import CommsConsoleHelper
from src.Modules.MessageParsing.fcb_message_parsing import (
    lat_lon_decimal_minutes_to_decimal_degrees,
)
from src.Modules.module_core import ThreadedModuleCore
from src.python_avionics.exceptions import SerialPortDisconnectedError
from src.python_avionics.model.fcb_cli import FcbCli
from src.python_avionics.model.serial_port import SerialPort


class FCBOffloadModule(ThreadedModuleCore):
    def __init__(self):
        self.nextCheckTime = time.time()
        self.primary_module = False

        super().__init__()

        self.serial_port_name = ""
        self.serial_connection = False
        self.python_avionics_fcb_cli = FcbCli(None)
        self.updatePythonAvionicsSerialPort()

        self.command_queue = []

        self.serial_devices["FCB USB Connection"] = self.changeActiveSerialPort

        self.callback_handler.addCallback(Constants.cli_interface_usb_command_key, self.cliCommand)

        self.cliConsole = CommsConsoleHelper(Constants.new_usb_cli_message_key)

        self.replay_dict: Dict[str, List[float]] = None
        self.replay_idx: int = 0
        self.replay_len = 0
        self.replay_name_to_path = {}

    def changeActiveSerialPort(self, portName):
        self.serial_port_name = portName
        self.serial_connection = False

    def closeSerialPort(self):
        if self.python_avionics_fcb_cli.serial_port is not None:
            self.python_avionics_fcb_cli.serial_port.port.close()

    def updatePythonAvionicsSerialPort(self):
        # Respect waiting time to not spam the console
        if not self.nextCheckTime <= time.time():
            return

        if len(self.serial_port_name) < 1:
            # blank name, try again later
            self.nextCheckTime = time.time() + 2
            self.serial_connection = False
            return

        try:
            self.logger.info(
                "Attempting to connect to FCB over USB at port {}".format(self.serial_port_name),
            )
            self.closeSerialPort()
            port_object = SerialPort(self.serial_port_name)
            self.python_avionics_fcb_cli.serial_port = port_object
            self.serial_connection = True
            self.logger.info(
                "Successfully connected to FCB over USB at port {}".format(self.serial_port_name),
            )
            port_object.port.flushInput()
            port_object.port.flushOutput()
        except Exception as e:
            self.logger.error("Unable to connect to FCB over USB at port {0}: {1}".format(self.serial_port_name, str(e)))
            self.nextCheckTime = time.time() + 4
            self.serial_connection = False

    def cliCommand(self, command):
        """Callback function to run from the GUI"""
        if self.enabled:
            self.command_queue.append(command)
        else:
            self.cliConsole.manualAddEntry("FCB USB offload module not enabled, can not run commands", False)

    def getOffloadKey(self, key):
        return self.replay_dict[f"offload_{key}"][0][self.replay_idx]

    def spin(self):
        if not self.serial_connection:
            self.updatePythonAvionicsSerialPort()

        if len(self.command_queue) > 0:
            command = self.command_queue.pop(0)
            self.cliConsole.manualAddEntry(command, False)
            self.data_dictionary[Constants.cli_interface_usb_command_running] = True
            ret = self.runCLICommand(command)

            if ret is not None:
                if "Available flights to offload" in ret:  # Check and see if we have a list of flights, and update the database dictionary
                    self.data_dictionary[Constants.cli_flights_list_key] = ret

                self.cliConsole.autoAddEntry(ret, True)

            # Report command done by broadcasting the result string, and also setting running back to false
            self.callback_handler.requestCallback(Constants.cli_interface_usb_result_key, ret)
            self.data_dictionary[Constants.cli_interface_usb_command_running] = False

        # Hack recorded data directly into the GUI pretending like it's full rate telemetry
        if self.replay_dict is not None:
            if self.replay_idx >= self.replay_len:
                self.replay_dict = None
            else:
                # create a dict from recorded data
                # This is SUCH A HACK. at each key we have a (data, time) array
                lat = self.getOffloadKey("gps_lat")
                long = self.getOffloadKey("gps_long")
                alt = self.getOffloadKey("pos_z")
                gpsalt = self.getOffloadKey("gps_alt")

                vel = self.getOffloadKey("vel_z")

                quat = [
                    self.getOffloadKey("q_w"),
                    self.getOffloadKey("q_x"),
                    self.getOffloadKey("q_y"),
                    self.getOffloadKey("q_z"),
                ]  # W X Y Z

                [roll, pitch, yaw] = quaternion_to_euler_angle(quat)

                lat = lat_lon_decimal_minutes_to_decimal_degrees(lat)
                long = lat_lon_decimal_minutes_to_decimal_degrees(long)

                dictionary = {
                    Constants.latitude_key: lat,
                    Constants.longitude_key: long,
                    Constants.altitude_key: alt,
                    Constants.gps_alt_key: gpsalt,
                    Constants.orientation_quaternion_key: quat,
                    Constants.vertical_speed_key: vel,
                    "roll": roll,
                    "pitch": pitch,
                    "yaw": yaw,
                }
                self.data_dictionary.update(dictionary)

            self.replay_idx += 1
            time.sleep(0.015)
        else:
            time.sleep(0.1)

    def runsEveryLoop(self):
        self.data_dictionary[Constants.cli_interface_usb_command_key] = self.cliConsole.getList()

    def runCLICommand(self, command):
        """Function to tell python_avionics to run the cli command, and handle states where the serial port isn't open"""
        if self.serial_connection:
            try:
                ret = self.python_avionics_fcb_cli.run_command(command)
                print(f"Successfully ran {command}")
                return ret
            except (IOError, SerialPortDisconnectedError) as e:
                self.serial_connection = False
                return "Lost connection to FCB: {}".format(e)
            except Exception as e:
                return "Unable to run command: {}".format(e)
        else:
            return "Unable to run command: FCB not connected over USB"

    def getDataDictionary(self):
        """
        Override this function to allow us to return the database dict while disabled
        """
        temporary_dict = self.data_dictionary.copy()
        self.data_dictionary = {}
        return temporary_dict

    def runOnEnableAndDisable(self):
        if not self.enabled:
            return

        mypath = "output"
        if not os.path.exists(mypath):
            return []
        all_post_processed_files = [f for f in listdir(mypath) if isfile(join(mypath, f)) and (f.endswith("-output-FCB-post.csv") or f.endswith("-output-post.csv"))]

        for file in all_post_processed_files:
            print(f"Loading flight {file}")
            runName = file.replace("-output-post.csv", "")
            runName = runName.replace("-output-FCB-post.csv", "")

            self.replay_name_to_path[runName] = join(mypath, file)
            if runName not in self.recorded_data_dictionary:
                self.recorded_data_dictionary[runName] = {}

    def getSpecificRun(self, run_name):
        # get specific run is called before setSpecificRunSelected
        # so return the actual data dict here, then make setSpecificRunSelected just save it

        self.logger.debug(f"run {run_name} requested")

        # Nuke old dictionary
        for key in self.recorded_data_dictionary:
            if key is not run_name:
                self.recorded_data_dictionary[key] = {}

        # Actually load the data file
        df = pd.read_csv(self.replay_name_to_path[run_name], index_col=0)

        if "timestamp_s" in df:
            time_series = df["timestamp_s"]  # no longer /1000
        elif "timestamp_ms" in df:
            time_series = df["timestamp_ms"] / 1000
        else:
            self.logger.error(f"No time series in run {run_name}?")
            return
        time_series = time_series - time_series.iloc[0]

        for key in df.keys():
            key = str(key)
            # Filter out IMU and high-g accelerometer raw count columns
            if ("imu" in key and "_real" not in key) or ("high_g" in key and "_real" not in key):
                continue

            # Put column into our data dictionary prefixed with offload_
            self.recorded_data_dictionary[run_name]["offload_" + key] = [list(df[key]), list(time_series)]
        self.recorded_data_dictionary[run_name]["keys"] = df.keys()

        return super().getSpecificRun(run_name)

    def setSpecificRunSelected(self, run_name):
        """
        Reset this widget's internal state in order to translate a FCB log file into the GUI
        """
        self.replay_dict = self.recorded_data_dictionary[run_name]
        self.replay_idx = 0
        self.replay_len = len(list(self.replay_dict.values())[0][0])
