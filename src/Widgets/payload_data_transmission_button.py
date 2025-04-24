from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QVBoxLayout

from src.constants import Constants
from src.Widgets.custom_q_widget_base import CustomQWidgetBase


class PayloadDataTransmissionButton(CustomQWidgetBase):
    def __init__(self, parent=None, arduino_interface=None):
        super().__init__(parent)

        self.arduino_interface = arduino_interface
        self.is_checked = 1  # 1 for transmitting data

        # Create and configure the toggle button
        self.button = QPushButton("Data Transmission ON", self)
        self.button.setFont(QFont("Arial", 20))
        self.button.setCheckable(True)
        self.button.setChecked(True)
        self.button.toggled.connect(self.toggle_state)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.setMinimumSize(200, 200)

        # Store button state in source key
        self.addSourceKey("payload_data_transmission_button", int, Constants.payload_data_transmission_button_key, hide_in_drop_down=True)

    def toggle_state(self, checked):
        """Toggle button text and update stored value."""
        self.is_checked = 1 if checked else 0
        self.button.setText("Data Transmission is on!" if checked else "Data Transmission is off!")
        self.updated_data_dictionary["payload_data_transmission_button"] = self.is_checked

        if self.arduino_interface:
            if self.is_checked == 1:
                self.arduino_interface.write_arduino_data("b")  # ON
            else:
                self.arduino_interface.write_arduino_data("s")  # OFF

    def updateData(self, vehicle_data, updated_data):
        """Update button state based on internal is_checked flag."""
        if self.is_checked:
            self.button.setChecked(True)
        else:
            self.button.setChecked(False)
