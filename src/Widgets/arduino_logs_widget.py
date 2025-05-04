from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

from src.constants import Constants
from src.Widgets.custom_q_widget_base import CustomQWidgetBase


class ArduinoLogsWidget(CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None):
        super().__init__(parent_widget)

        self.arduino_log_label = QTextEdit("Arduino Received Data Log", self)
        self.arduino_log_label.setAlignment(Qt.AlignCenter)
        self.last_log = ""

        vbox = QVBoxLayout()
        self.title_label = QLabel("Arduino Received Data Log \n", self)
        self.title_label.setAlignment(Qt.AlignCenter)  # Use Qt.AlignCenter for alignment
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        vbox.addWidget(self.title_label)
        vbox.addWidget(self.arduino_log_label)
        self.setLayout(vbox)
        self.addSourceKey("payload_logs", str, "payload_logs", default_value=False, hide_in_drop_down=True)

    def updateData(self, vehicle_data, updated_data):
        payload_log = self.getDictValueUsingSourceKey("payload_logs")
        payload_log = str(payload_log)
        # print("payload log in arduino logs is", payload_log)
        if payload_log != self.last_log:
            self.last_log = payload_log
            print("last log:", self.last_log)
            print("current log:", payload_log)
            self.arduino_log_label.setText(payload_log)
            self.arduino_log_label.setStyleSheet("font-size: 20px; font-weight: bold;")
            self.arduino_log_label.moveCursor(QTextCursor.End)

    def adjustSize(self) -> None:
        self.resize(500, 500)
