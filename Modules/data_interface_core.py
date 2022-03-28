"""
Base data interface
"""

import threading
import time


class ThreadedModuleCore(threading.Thread):
    """
    Spins up module in its own thread, and handles all cross-thread data transfer
    """

    def __init__(self):
        super().__init__()
        self.data_dictionary = {}
        self.gui_full_data_dictionary = {}
        self.recorded_data_dictionary = {}  # {run_name: {run_dict}}
        self.callbacks_to_add = [[]]
        self.should_be_running = True
        self.enabled = True
        self.was_enabled = True
        self.primary_module = False  # Only one module with this set to true should run at a time

        self.console_callback = None
        self.last_console_message = ""
        self.last_log_time = 0

        self.reconfigure_options_dictionary = {}

    def getCallbacksToAdd(self):
        return self.callbacks_to_add

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

    def setConsoleCallback(self, callback):
        self.console_callback = callback

    def logToConsoleAndCheck(self, value, level):
        """Logs to console if the message isn't the same as the last message"""
        if value != self.last_console_message:
            self.logToConsole(value, level)

    def logToConsole(self, value, level, override_disabled_check=False):
        """Logs data to GUI Console"""
        if self.enabled or override_disabled_check:
            self.console_callback("{0}: {1}".format(time.strftime("%H:%M:%S"), value), level)
            self.last_console_message = value

    def logToConsoleThrottle(self, value, level, interval):
        """Logs data to GUI Console once per interval"""
        if time.time() - interval > self.last_log_time:
            self.logToConsole(value, level)
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
            time.sleep(0.01)  # Keep python from locking the database objects all the time
        self.closeOut()

    def startUp(self):
        """Runs once the thread starts before anything else"""
        pass

    def runOnEnableAndDisable(self):
        pass

    def spin(self):
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
