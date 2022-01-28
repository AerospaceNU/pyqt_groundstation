"""
Specific widget to display ROV status
"""

from PyQt5.QtWidgets import QWidget, QGridLayout

from Widgets import custom_q_widget_base

from Widgets.QWidget_Parts import simple_bar_graph_widget

from data_helpers import get_value_from_dictionary


class ControlStationStatus(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, widget: QWidget = None):
        super().__init__(widget)
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

    def updateControlStationData(self, csData):
        battery = float(get_value_from_dictionary(csData, "battery", -1))
        ram = float(get_value_from_dictionary(csData, "ram", -1))
        cpu = float(get_value_from_dictionary(csData, "cpu", -1))
        disk = float(get_value_from_dictionary(csData, "disk", -1))

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
