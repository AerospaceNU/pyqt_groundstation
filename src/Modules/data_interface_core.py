"""
Base class for a module

All modules added to the GUI NEED to extend this class (or one of its subclasses) in order to function.
"""

import threading
import time

from src.CustomLogging.dpf_logger import MAIN_GUI_LOGGER


class ThreadedModuleCore(threading.Thread):
    """
    Base class for a module.  All modules added to the GUI NEED to extend this class (or one of its subclasses) in order to function.
    This class spins up a new thread to run the module code in, and handles cross-thread data transfer so callbacks are called in the correct thread (I think)

    The two most important methods here to override for new modules are the runOnEnableAndDisable() method and the spin() method.
    runOnEnableAndDisable() runs whenever the module is enabled or disabled, and spin runs once every .01 seconds at maximum.

    This class also provides an interface for supplying pre-recorded time-series data to the GUI.
    """

    def __init__(self):
        super().__init__()
        self.logger = MAIN_GUI_LOGGER.get_logger(self.__class__.__name__)
        self.data_dictionary = {}
        self.gui_full_data_dictionary = {}
        self.recorded_data_dictionary = {}  # {run_name: {run_dict}}
        self.callbacks_to_add = [[]]
        self.serial_devices = {}
        self.should_be_running = True
        self.enabled = True
        self.was_enabled = True
        self.primary_module = False  # Only one module with this set to true should run at a time

        self.last_console_message = ""
        self.last_log_time = 0

        self.reconfigure_options_dictionary = {}

    def getCallbacksToAdd(self):
        """DO NOT OVERRIDE.  Provides a list of callbacks to DPFGUI"""
        return self.callbacks_to_add

    def getSerialDevices(self):
        """Returns a dict that is {device_name: callback_function(str: portname)} that contains all the serial devices added by this module"""
        return self.serial_devices

    def getReconfigureDictionary(self):
        return self.reconfigure_options_dictionary

    def getSpecificRun(self, run_name):
        if run_name in self.recorded_data_dictionary:
            return self.recorded_data_dictionary[run_name]
        else:
            return {}

    def getRunNames(self):
        return list(self.recorded_data_dictionary.keys())

    def hasRecordedData(self):
        return bool(self.recorded_data_dictionary)

    def setSpecificRunSelected(self, run_name):
        """ Override to provide custon replay functionality"""
        pass

    def logToConsoleAndCheck(self, message, level):
        """Logs to console if the message isn't the same as the last message"""
        if message != self.last_console_message:
            self.logger.log(level, message)

    def logToConsoleThrottle(self, message, level, interval):
        """Logs data to GUI Console once per interval"""
        if time.time() - interval > self.last_log_time:
            self.logger.log(level, message)
            self.last_log_time = time.time()

    def setEnabled(self, enabled):
        self.enabled = enabled

    def toggleEnabled(self):
        self.setEnabled(not self.enabled)

    def run(self):
        """
        Runs in thread when start() is called
        """
        self.startUp()
        while self.should_be_running:
            if self.enabled != self.was_enabled:  # If the enabled state changes, run the method for that
                self.runOnEnableAndDisable()
                self.was_enabled = self.enabled

            if self.enabled:
                self.spin()
            self.runsEveryLoop()
            time.sleep(0.01)  # Keep python from locking the database objects all the time
        self.closeOut()

    def startUp(self):
        """Runs once the thread starts before anything else"""
        pass

    def runOnEnableAndDisable(self):
        pass

    def spin(self):
        """
        Runs while enabled
        This is the primary place to add functionality
        """
        pass

    def runsEveryLoop(self):
        """
        Runs while enabled or disabled
        Use this sparingly
        """
        pass

    def closeOut(self):
        """Called when the module shuts down"""
        pass

    def stop(self):
        self.should_be_running = False

    def setFullDataDictionary(self, data_dict):
        """
        Allows the GUI to give each interface the full database dictionary
        This feels like a hack, but I don't have a great alternative right now
        """

        self.gui_full_data_dictionary = data_dict

    def getDataDictionary(self):
        if self.enabled:
            temporary_dict = self.data_dictionary.copy()
            self.data_dictionary = {}
            return temporary_dict
        else:
            return {}
