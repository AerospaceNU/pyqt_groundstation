import time

from python_avionics.model.fcb_cli import FcbCli
from python_avionics.model.serial_port import SerialPort

from Modules.data_interface_core import ThreadedModuleCore
from Modules.DataInterfaceTools.comms_console_helper import CommsConsoleHelper
from constants import Constants


class FCBOffloadModule(ThreadedModuleCore):
    def __init__(self):
        super().__init__()

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

    def updatePythonAvionicsSerialPort(self):
        try:
            self.logToConsole("Attempting to connect to FCB over USB at port {}".format(self.serial_port_name), 1, True)
            port_object = SerialPort(self.serial_port_name)
            self.python_avionics_fcb_cli.serial_port = port_object
            self.serial_connection = True
            self.logToConsole("Successfully connected to FCB over USB at port {}".format(self.serial_port_name), 1, True)
        except:
            self.logToConsole("Unable to connect to FCB over USB at port {}".format(self.serial_port_name), 2, True)
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
            print("running command [{}]".format(command))
            try:
                ret = self.python_avionics_fcb_cli.run_command(command)
                return ret
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
