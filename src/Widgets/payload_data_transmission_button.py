from PyQt5.QtWidgets import QPushButton, QVBoxLayout
from src.Widgets.custom_q_widget_base import CustomQWidgetBase
from src.constants import Constants

class PayloadDataTransmissionButton(CustomQWidgetBase):
    def __init__(self, parent=None, arduino_interface=None):
        super().__init__(parent)
        
        self.arduino_interface = arduino_interface
        # Create a toggle button
        self.button = QPushButton("Data Transmission ON", self)
        self.button.setCheckable(True)  # Enable toggle functionality
        self.button.toggled.connect(self.toggle_state)  # Connect signal to slot

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.setMinimumSize(200, 200)

        # Store button state in source key
        self.addSourceKey(
            "payload_data_transmission_button", int, 
            Constants.payload_read_write_button, 
            default_value=1, hide_in_drop_down=True
        )

    def toggle_state(self, checked):
        """Toggle button text and update stored value."""
        new_state = 1 if checked else 0
        self.button.setText("Data Transmission ON" if checked else "Data Transmission OFF")  # Correct button text

        # Update the stored value
        self.setSourceKeyValue("payload_data_transmission_button", new_state)
        if self.arduino_interface:
            if new_state == 1:
                self.arduino_interface.write_arduino_data("b")  # Data Transmission ON, send 'b'
            else:
                self.arduino_interface.write_arduino_data("s")  # Data Transmission OFF, send 's'

    def updateData(self, vehicle_data, updated_data):
        """Update button state based on external data source."""
        button_val = self.getDictValueUsingSourceKey("payload_data_transmission_button")
        if button_val:
            self.button.setChecked(True)
        else:
            self.button.setChecked(False)
