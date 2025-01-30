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

class PayloadTemperatureWidget(CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None, source_list=None, default_temperature=0):
        super().__init__(parent_widget)
        
        self.payload_temp_graph = simple_bar_graph_widget.SimpleBarGraphWidget(title="Payload Temp", minValue=0, maxValue=100)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.payload_temp_graph)
        self.setLayout(vbox)
        # self.widgeztSize = 20
        self.title = "Payload Temp"
        self.addSourceKey("payload_temp", float, Constants.payload_temperature_key, default_value=0, hide_in_drop_down=True)
        self.addSourceKey("fcb_voltage", float, Constants.fcb_battery_voltage, -1, hide_in_drop_down=True)
    #     self.temperature_value = QLabel(f"{default_temperature}°C", self)
    #     self.temperature_header = QLabel("Payload Temperature", self)
        
    #     self.recorded_data_mode = False
    #     self.record_new_data = True
        
    #     self.payload_temp = default_temperature
        
    #     temperature_font = QFont()
    #     temperature_font.setPointSize(50)
    #     label_font = QFont()
    #     label_font.setPointSize(30)
    #     self.temperature_value.setFont(temperature_font)
    #     self.temperature_header.setFont(label_font) # not changing fonts whyyyyyyy
    #     self.temperature_value.setAlignment(Qt.AlignCenter)
    #     self.temperature_header.setAlignment(Qt.AlignHCenter)
    #     # self.data_dictionary = {'payload': {'payload_temp': 40.0}}
    #     # self.data_dictionary = self.updateData()
    #     self.addSourceKey("payload_temp", float, Constants.payload_temperature_key, default_value=0, hide_in_drop_down=True)
    #     self.addSourceKey("fcb_voltage", float, Constants.fcb_battery_voltage, -1, hide_in_drop_down=True)
    # #       payload_key = "payload"
    # # payload_temperature_key = "temperature"

    #     layout = QVBoxLayout(self)

    #     layout.addWidget(self.temperature_header)
    #     layout.addStretch(1)
    #     layout.addWidget(self.temperature_value)

    #     layout.addStretch(1)

    #     layout.setAlignment(Qt.AlignHCenter)  
    #     self.setLayout(layout)

    #     self.setMinimumSize(150, 150)
    
    #     if source_list is None:
    #         source_list = [] 
                
    def setPlaybackMode(self, use_recorded_data):  
        self.recorded_data_mode = use_recorded_data
    
    def setEnabled(self, enabled):
        self.record_new_data = enabled
    
    def updateData(self, vehicle_data, updated_data):
        temp = self.getDictValueUsingSourceKey("payload_temp")
        # print(f"temp!!!!!!!!!! {temp}")
        self.temperature_value = QLabel(f"{temp}°C", self)
        self.payload_temp_graph.setValue(temp)