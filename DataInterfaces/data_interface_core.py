"""
Base data interface
"""

import threading
import time



class DataInterfaceCore(threading.Thread):
    def __init__(self):
        super().__init__()
        self.data_dictionary = {}
        self.should_be_running = True
        self.enabled = True

        self.console_callback = None
        self.last_console_message = ""

    def setConsoleCallback(self, callback):
        self.console_callback = callback

    def logToConsoleAndCheck(self, value, level):
        """Logs to console if the message isn't the same as the last message"""
        if value != self.last_console_message:
            self.logToConsole(value, level)

    def logToConsole(self, value, level):
        """Logs data to GUI Console"""
        if self.enabled:
            self.console_callback("{0}: {1}".format(time.strftime("%H:%M:%S"), value), level)
            self.last_console_message = value

    def setEnabled(self, enabled):
        self.enabled = enabled

    def run(self):
        while self.should_be_running:
            self.spin()
            time.sleep(0.01)  # Keep python from locking the database objects all the time

    def stop(self):
        self.should_be_running = False

    def spin(self):
        pass

    def getDataDictionary(self):
        if self.enabled:
            return self.data_dictionary
        else:
            return {}
