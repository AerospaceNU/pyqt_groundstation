from datetime import timedelta

from PyQt5.QtCore import Qt, QTime
from PyQt5.QtWidgets import QApplication, QLabel, QLCDNumber, QVBoxLayout, QWidget

from src.constants import Constants
from src.Widgets.custom_q_widget_base import CustomQWidgetBase
from src.Widgets.QWidget_Parts import simple_bar_graph_widget


class PayloadLandingTimeWidget(CustomQWidgetBase):
    def __init__(self, parent=None, default_time=0):
        super().__init__(parent)

        # Create Title Label
        self.title_label = QLabel("Landing Time", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")

        # Create LCD Display
        self.lcd = QLCDNumber(self)
        self.lcd.setDigitCount(8)  # Display HH:MM:SS
        self.lcd.setStyleSheet("background-color: white; color: green; border: 2px solid green;")
        self.lcd.setSegmentStyle(QLCDNumber.Flat)

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.lcd)

        self.setLayout(layout)
        self.setMinimumSize(200, 200)

        self.addSourceKey("payload_landing_time", float, Constants.payload_landing_time_key, default_value=0, hide_in_drop_down=True)

    def updateData(self, vehicle_data, updated_data):
        landing_time = self.getDictValueUsingSourceKey("payload_landing_time")
        landing_time = max(0, int(float(landing_time)))  # Ensure non-negative time
        formatted_time = QTime(0, 0).addSecs(landing_time).toString("HH:mm:ss")
        self.lcd.display(formatted_time)
