from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.Widgets.custom_q_widget_base import CustomQWidgetBase
from src.Modules.random_data_interface import RandomDataInterface
from src.Modules.module_core import ThreadedModuleCore
from src.constants import Constants
import math
import time
from src.data_helpers import check_type, first_index_in_list_larger_than, get_value_from_dictionary

from PyQt5 import QtCore
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from src.constants import Constants
from src.data_helpers import round_to_string
from src.Widgets import custom_q_widget_base
from src.Widgets.QWidget_Parts import simple_bar_graph_widget

class PayloadBatteryWidget(CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None, source_list=None, default_temperature=0):
        super().__init__(parent_widget)
        self.payload_battery_graph = simple_bar_graph_widget.SimpleBarGraphWidget(title="Payload Battery", minValue=0, maxValue=100)
        vbox = QVBoxLayout()
        vbox.addWidget(self.payload_battery_graph)
        self.setLayout(vbox)
        self.setMaximumSize(100,200)
        # self.widgeztSize = 20
        self.title = "Payload Battery"
        self.addSourceKey("payload_battery", float, Constants.payload_battery_key, default_value=0, hide_in_drop_down=True)
        self.adjustSize()

                
    def setPlaybackMode(self, use_recorded_data):  
        self.recorded_data_mode = use_recorded_data
    
    def setEnabled(self, enabled):
        self.record_new_data = enabled
    
    def updateData(self, vehicle_data, updated_data):
        payload_battery = self.getDictValueUsingSourceKey("payload_battery")
        self.payload_battery_value = QLabel(f"{payload_battery}%", self)
        self.payload_battery_graph.setValue(payload_battery)
        
    def adjustSize(self) -> None:
        self.resize(100, 200)
