import time

from python_avionics.model.fcb_cli import FcbCli
from python_avionics.model.serial_port import SerialPort

from Modules.data_interface_core import ThreadedModuleCore
from Modules.DataInterfaceTools.comms_console_helper import CommsConsoleHelper
from constants import Constants


class FCBOffloadModule(ThreadedModuleCore):
    """
    """

    def __init__(self):
        super().__init__()

        self.serial_port_name = ""
        self.serial_connection = False
        self.python_avionics_fcb_cli = FcbCli(None)
        self.updatePythonAvionicsSerialPort()

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
        except:
            self.logToConsole("Unable to connect to FCB over USB at port {}".format(self.serial_port_name), 2, True)
            self.serial_connection = False

    def cliCommand(self, command):
        """Callback function to run from the GUI"""
        if self.enabled:
            ret = self.runCLICommand(command)
            print(ret)

    def spin(self):
        if not self.serial_connection:
            self.updatePythonAvionicsSerialPort()

        time.sleep(1)

    def runCLICommand(self, command):
        """Function to tell python_avionics to run the cli command, and handle states where the serial port isn't open"""
        if self.serial_connection:
            print("running command [{}]".format(command))
            ret = self.python_avionics_fcb_cli.run_command(command)
            print(ret)
            return ret
        else:
            return "Unable to run command: FCB not connected over USB"
