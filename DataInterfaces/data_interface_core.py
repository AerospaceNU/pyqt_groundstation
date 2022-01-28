"""
Base data interface
"""

import threading
import time


class DataInterfaceCore(threading.Thread):
    def __init__(self):
        super().__init__()
        self.data_dictionary = {}
        self.is_running = True

    def run(self):
        while self.is_running:
            self.spin()
            time.sleep(0.01)  # Keep python from locking the database objects all the time

    def stop(self):
        self.is_running = False

    def spin(self):
        pass

    def getDataDictionary(self):
        return self.data_dictionary
