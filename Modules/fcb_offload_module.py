import time

from python_avionics.model.fcb_cli import FcbCli
from python_avionics.model.serial_port import SerialPort

from Modules.data_interface_core import ThreadedModuleCore
from constants import Constants


class FCBOffloadModule(ThreadedModuleCore):
    """
    Measures important stats from laptop
    """

    def __init__(self):
        super().__init__()

        self.serial_port_name = ""
        self.serial_connection = False
        self.python_avionics_fcb_cli = FcbCli(None, self.pythonAvionicsCallback)
        self.updatePythonAvionicsSerialPort()

        self.serial_devices["FCB USB Connection"] = self.changeActiveSerialPort

        self.callbacks_to_add.append([Constants.cli_interface_key, self.cliCommand])

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

    def pythonAvionicsCallback(self, str_arr):
        print(str_arr)
        return 0

    def cliCommand(self, command):
        print(command)

    def spin(self):
        if not self.serial_connection:
            self.updatePythonAvionicsSerialPort()

        time.sleep(1)
