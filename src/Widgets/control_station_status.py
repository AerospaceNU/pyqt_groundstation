"""
Specific widget to display ROV status
"""

from PyQt5.QtWidgets import QGridLayout, QWidget

from src.constants import Constants
from src.data_helpers import get_value_from_dictionary
from src.Widgets import custom_q_widget_base
from src.Widgets.QWidget_Parts import simple_bar_graph_widget


class ControlStationStatus(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.BatteryStatus = simple_bar_graph_widget.SimpleBarGraphWidget(title="Battery", minValue=0, maxValue=100)
        self.DiskStatus = simple_bar_graph_widget.SimpleBarGraphWidget(title="Disk", minValue=0, maxValue=100)
        self.RamStatus = simple_bar_graph_widget.SimpleBarGraphWidget(title="Ram", minValue=0, maxValue=100)
        self.CPUStatus = simple_bar_graph_widget.SimpleBarGraphWidget(title="CPU", minValue=0, maxValue=100)

        layout = QGridLayout()
        layout.setVerticalSpacing(0)
        layout.addWidget(self.BatteryStatus, 1, 1)
        layout.addWidget(self.CPUStatus, 1, 2)
        layout.addWidget(self.RamStatus, 1, 3)
        layout.addWidget(self.DiskStatus, 1, 4)
        self.setLayout(layout)

    def updateData(self, vehicle_data, updated_data):
        battery = float(get_value_from_dictionary(vehicle_data, Constants.laptop_battery_percent_key, -1))
        ram = float(get_value_from_dictionary(vehicle_data, Constants.laptop_ram_usage_key, -1))
        cpu = float(get_value_from_dictionary(vehicle_data, Constants.laptop_cpu_usage_key, -1))
        disk = float(get_value_from_dictionary(vehicle_data, Constants.laptop_disk_usage_key, -1))

        scale = 0.7
        self.BatteryStatus.fixWidth(scale)
        self.CPUStatus.fixWidth(scale)
        self.RamStatus.fixWidth(scale)
        self.DiskStatus.fixWidth(scale)

        self.BatteryStatus.setValue(battery)
        self.CPUStatus.setValue(cpu)
        self.RamStatus.setValue(ram)
        self.DiskStatus.setValue(disk)

        self.setMaximumWidth(self.BatteryStatus.width() * 4 + 30)

    def customUpdateAfterThemeSet(self):
        for widget in [self.BatteryStatus, self.DiskStatus, self.RamStatus, self.CPUStatus]:
            widget.setTextColor(self.palette().text().color())
