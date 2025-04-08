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
            Constants.payload_data_transmission_button_key, 
            hide_in_drop_down=True
        )

        self.is_checked = 1 # 1 for transmitting data
        
    def toggle_state(self, checked):
        """Toggle button text and update stored value."""
        print("Calling toggl state")
        self.is_checked = 1 if checked else 0
        self.button.setText("Data Transmission is on!" if checked else "Data Transmission is off!")  # Correct button text
        self.updated_data_dictionary["payload_data_transmission_button"] = self.is_checked
        # print(f"self updated: {self.updated_data_dictionary['payload_data_transmission_button']}, should be {self.is_checked}")
        # print("BEW STATEEEEE", {self.is_checked})
        # self.updateData(vehicle_data=None, updated_data=None)
        if self.arduino_interface:
            if self.is_checked == 1:
                self.arduino_interface.write_arduino_data("b")  # Data Transmission ON, send 'b'
            else:
                self.arduino_interface.write_arduino_data("s")  # Data Transmission OFF, send 's'



    def updateData(self, vehicle_data, updated_data):
        """Update button state based on external data source."""
        # print("update data getting called here!")
        # button_val = self.getDictValueUsingSourceKey("payload_data_transmission_button")
        # if self.is_checked != None:
        #     print("button val is not none")
        if self.is_checked:
            # print("there is a button val")
            self.button.setChecked(True)
        else:
            self.button.setChecked(False)
            # print("there is not a button val")

