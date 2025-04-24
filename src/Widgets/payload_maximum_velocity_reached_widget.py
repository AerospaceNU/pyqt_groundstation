from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.constants import Constants
from src.Widgets.custom_q_widget_base import CustomQWidgetBase


class PayloadMaximumVelocity(CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None):
        super().__init__(parent_widget)

        self.max_vel_label = QLabel("Maximum Velocity", self)
        self.max_vel_label.setAlignment(Qt.AlignCenter)

        vbox = QVBoxLayout()
        vbox.addWidget(self.max_vel_label)
        self.setLayout(vbox)

        self.title = "Maximum Velocity"
        self.addSourceKey("payload_max_velocity", float, Constants.payload_max_velocity_key, default_value=False, hide_in_drop_down=True)

    def updateData(self, vehicle_data, updated_data):
        payload_max_velocity = self.getDictValueUsingSourceKey("payload_max_velocity")
        self.max_vel_label.setText(f"Max Velocity\n Reached\n \n \n {payload_max_velocity} m/s")
        self.max_vel_label.setStyleSheet("font-size: 20px; font-weight: bold;")

    def adjustSize(self) -> None:
        self.resize(250, 200)
