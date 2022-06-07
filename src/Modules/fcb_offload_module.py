import os
import time
from os import listdir
from os.path import isfile, join

import pandas as pd

from src.constants import Constants
from src.Modules.data_interface_core import ThreadedModuleCore
from src.Modules.DataInterfaceTools.comms_console_helper import CommsConsoleHelper
from src.python_avionics.exceptions import SerialPortDisconnectedError
from src.python_avionics.model.fcb_cli import FcbCli
from src.python_avionics.model.serial_port import SerialPort


class FCBOffloadModule(ThreadedModuleCore):
    def __init__(self):
        super().__init__()
        self.primary_module = True

        self.serial_port_name = ""
        self.serial_connection = False
        self.python_avionics_fcb_cli = FcbCli(None)
        self.updatePythonAvionicsSerialPort()

        self.command_queue = []

        self.serial_devices["FCB USB Connection"] = self.changeActiveSerialPort

        self.callbacks_to_add.append([Constants.cli_interface_usb_key, self.cliCommand])

        self.cliConsole = CommsConsoleHelper()

    def changeActiveSerialPort(self, portName):
        self.serial_port_name = portName
        self.serial_connection = False

    def closeSerialPort(self):
        if self.python_avionics_fcb_cli.serial_port is not None:
            self.python_avionics_fcb_cli.serial_port.port.close()

    def updatePythonAvionicsSerialPort(self):
        try:
            self.logToConsole(
                "Attempting to connect to FCB over USB at port {}".format(self.serial_port_name),
                1,
                True,
            )
            self.closeSerialPort()
            port_object = SerialPort(self.serial_port_name)
            self.python_avionics_fcb_cli.serial_port = port_object
            self.serial_connection = True
            self.logToConsole(
                "Successfully connected to FCB over USB at port {}".format(self.serial_port_name),
                1,
                True,
            )
            port_object.port.flushInput()
            port_object.port.flushOutput()
        except Exception:
            self.logToConsole(
                "Unable to connect to FCB over USB at port {0}".format(self.serial_port_name),
                2,
                True,
            )
            self.serial_connection = False

    def cliCommand(self, command):
        """Callback function to run from the GUI"""
        if self.enabled:
            self.command_queue.append(command)
        else:
            self.cliConsole.manualAddEntry("FCB USB offload module not enabled, can not run commands", False)

    def spin(self):
        if not self.serial_connection:
            self.updatePythonAvionicsSerialPort()

        if len(self.command_queue) > 0:
            command = self.command_queue.pop(0)
            self.cliConsole.manualAddEntry(command, False)
            ret = self.runCLICommand(command)

            if ret is not None:
                if "Available flights to offload" in ret:  # Check and see if we have a list of flights, and update the database dictionary
                    self.data_dictionary[Constants.cli_flights_list_key] = ret

                self.cliConsole.autoAddEntry(ret, True)

        time.sleep(0.1)

    def runsEveryLoop(self):
        self.data_dictionary[Constants.cli_interface_usb_key] = self.cliConsole.getList()

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
        all_post_processed_files = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith("-output-post.csv")]

        for file in all_post_processed_files:
            print(f"Loading flight {file}")
            runName = file.replace("-output-post.csv", "")
            df = pd.read_csv(join(mypath, file), index_col=0)

            time_series = df["timestamp_s"] / 1000.0

            if runName not in self.recorded_data_dictionary:
                self.recorded_data_dictionary[runName] = {}

            # self.recorded_data_dictionary[runName][Constants.altitude_key] = [list(df['pos_z']), list(time_series)]
            # return

            # TOTAL HACK, but the member names are the same as what the FCB expects
            # and the member values are keys in the dataframe
            offload_map = [a for a in dir(Constants.OffloadConstants) if not a.startswith("__")]
            for key in offload_map:
                self.recorded_data_dictionary[runName][getattr(Constants, key)] = [list(df[getattr(Constants.OffloadConstants, key)]), list(time_series)]