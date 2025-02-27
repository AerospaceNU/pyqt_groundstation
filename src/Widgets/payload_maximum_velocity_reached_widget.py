from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from src.Widgets.custom_q_widget_base import CustomQWidgetBase
from src.constants import Constants
from src.Widgets.QWidget_Parts import simple_bar_graph_widget
from PyQt5.QtWidgets import QGridLayout, QLabel

class PayloadMaximumVelocity(CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None, source_list=None, default_temperature=0):
        super().__init__(parent_widget)

        self.max_vel_label = QLabel("Maximum Velocity", self)
        self.max_vel_label.setAlignment(Qt.AlignCenter)

        vbox = QVBoxLayout()
        vbox.addWidget(self.max_vel_label)
        self.setLayout(vbox)

        self.title = "Payload Maximum Velocity"
        self.addSourceKey("payload_max_velocity", float, Constants.payload_max_velocity_key, default_value=False, hide_in_drop_down=True)
    
    def updateData(self,):
        payload_max_velocity= self.getDictValueUsingSourceKey("payload_max_velocity")
        self.max_vel_label.setText(f"Payload Max Velocity Reached: {payload_max_velocity} m/s")

    def adjustSize(self) -> None:
        self.resize(200, 200)
        
    