from PyQt5.QtWidgets import QVBoxLayout, QWidget

from src.constants import Constants
from src.Widgets.custom_q_widget_base import CustomQWidgetBase
from src.Widgets.QWidget_Parts import simple_bar_graph_widget


class PayloadBatteryWidget(CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None, source_list=None, default_temperature=0):
        super().__init__(parent_widget)
        self.payload_battery_graph = simple_bar_graph_widget.SimpleBarGraphWidget(title="Battery V", minValue=0, maxValue=20)

        vbox = QVBoxLayout()
        vbox.addWidget(self.payload_battery_graph)
        self.setLayout(vbox)
        self.setMaximumSize(100, 200)
        self.addSourceKey("payload_battery", float, Constants.payload_battery_key, default_value=0, hide_in_drop_down=True)
        self.adjustSize()

    def setPlaybackMode(self, use_recorded_data):
        self.recorded_data_mode = use_recorded_data

    def setEnabled(self, enabled):
        self.record_new_data = enabled

    def updateData(self, vehicle_data, updated_data):
        payload_battery = self.getDictValueUsingSourceKey("payload_battery")
        self.payload_battery_graph.setValue(payload_battery)

    def adjustSize(self) -> None:
        self.resize(100, 200)
