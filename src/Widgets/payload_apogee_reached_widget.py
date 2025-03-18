from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from src.Widgets.custom_q_widget_base import CustomQWidgetBase
from src.constants import Constants
from src.Widgets.QWidget_Parts import simple_bar_graph_widget
from PyQt5.QtWidgets import QGridLayout, QLabel

class PayloadApogeeAltitudeWidget(CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None, source_list=None, default_temperature=0):
        super().__init__(parent_widget)

        self.apogee_label = QLabel("Altitude", self)
        self.apogee_label.setAlignment(Qt.AlignCenter)

        vbox = QVBoxLayout()
        vbox.addWidget(self.apogee_label)
        self.setLayout(vbox)

        self.title = "Payload Apogee Status"
        self.addSourceKey("payload_apogee_altitude", float, Constants.payload_apogee_altitude_key, default_value=False, hide_in_drop_down=True)
    
    def updateData(self, vehicle_data, updated_data):
        payload_apogee_altitude= self.getDictValueUsingSourceKey("payload_apogee_altitude")
        self.apogee_label.setText(f"Payload Apogee Altitude Reached:\n \n \n {payload_apogee_altitude} m")

    def adjustSize(self) -> None:
        self.resize(250, 200)    
    