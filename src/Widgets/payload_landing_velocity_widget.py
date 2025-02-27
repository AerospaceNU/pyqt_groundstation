from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from src.Widgets.custom_q_widget_base import CustomQWidgetBase
from src.constants import Constants
from src.Widgets.QWidget_Parts import simple_bar_graph_widget
from PyQt5.QtWidgets import QGridLayout, QLabel

class PayloadLandingVelocity(CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None, source_list=None, default_temperature=0):
        super().__init__(parent_widget)

        self.landing_vel_label = QLabel("Landing Velocity", self)
        self.landing_vel_label.setAlignment(Qt.AlignCenter)

        vbox = QVBoxLayout()
        vbox.addWidget(self.landing_vel_label)
        self.setLayout(vbox)

        self.title = "Payload Landing Velocity"
        self.addSourceKey("payload_landing_velocity", float, Constants.payload_landing_velocity_key, default_value=False, hide_in_drop_down=True)
    
    def updateData(self, vehicle_data, updated_data):
        payload_landing_velocity= self.getDictValueUsingSourceKey("payload_landing_velocity")
        self.landing_vel_label.setText(f"Payload Landing Velocity: {payload_landing_velocity} m/s")

    def adjustSize(self) -> None:
        self.resize(200, 200)
        
    