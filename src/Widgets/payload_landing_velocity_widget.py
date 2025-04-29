from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.constants import Constants
from src.Widgets.custom_q_widget_base import CustomQWidgetBase


class PayloadLandingVelocity(CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None, source_list=None, default_temperature=0):
        super().__init__(parent_widget)

        self.landing_vel_label = QLabel("Landing Velocity", self)
        self.landing_vel_label.setAlignment(Qt.AlignCenter)

        vbox = QVBoxLayout()
        vbox.addWidget(self.landing_vel_label)
        self.setLayout(vbox)

        self.title = "Landing Velocity"
        self.addSourceKey("payload_landing_velocity", float, Constants.payload_landing_velocity_key, default_value=False, hide_in_drop_down=True)

    def updateData(self, vehicle_data, updated_data):
        payload_landing_velocity = self.getDictValueUsingSourceKey("payload_landing_velocity")
        self.landing_vel_label.setText(f"Landing Velocity\n \n {payload_landing_velocity} m/s")
        self.landing_vel_label.setStyleSheet("font-size: 20px; font-weight: bold;")

    def adjustSize(self) -> None:
        self.resize(200, 150)
