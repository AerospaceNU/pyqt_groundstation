import time

import psutil

from src.constants import Constants
from src.Modules.module_core import ThreadedModuleCore


class LaptopStatusMonitor(ThreadedModuleCore):
    """
    Measures important stats from laptop
    """

    def __init__(self):
        super().__init__()

    def spin(self):
        battery = psutil.sensors_battery()  # returns a tuple

        self.data_dictionary[Constants.laptop_cpu_usage_key] = psutil.cpu_percent()
        self.data_dictionary[Constants.laptop_ram_usage_key] = psutil.virtual_memory().percent
        self.data_dictionary[Constants.laptop_disk_usage_key] = psutil.disk_usage("/").percent

        if battery is not None:
            self.data_dictionary[Constants.laptop_battery_percent_key] = float(battery.percent)
            self.data_dictionary[Constants.laptop_battery_charging_key] = battery.power_plugged

        time.sleep(1)
