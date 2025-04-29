from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.constants import Constants
from src.Widgets.custom_q_widget_base import CustomQWidgetBase


class PayloadAccelerationWidget(CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None, source_list=None, default_temperature=0):
        super().__init__(parent_widget)

        self.apogee_label = QLabel("Acceleration", self)
        self.apogee_label.setAlignment(Qt.AlignCenter)

        vbox = QVBoxLayout()
        vbox.addWidget(self.apogee_label)
        self.setLayout(vbox)

        self.title = "Acceleration"
        self.addSourceKey("payload_acceleration", float, Constants.payload_acceleration_key, default_value=False, hide_in_drop_down=True)

    def updateData(self, vehicle_data, updated_data):
        payload_acceleration = self.getDictValueUsingSourceKey("payload_acceleration")
        self.apogee_label.setText(f"Acceleration \n \n {payload_acceleration} g force")
        self.apogee_label.setStyleSheet("font-size: 20px; font-weight: bold;")

    def adjustSize(self) -> None:
        self.resize(175, 150)
