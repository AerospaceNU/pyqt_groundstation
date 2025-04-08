from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton
from PyQt5.QtCore import Qt  # Import Qt from PyQt5.QtCore
from src.Widgets.custom_q_widget_base import CustomQWidgetBase
from src.constants import Constants

class PayloadUserInputWidget(CustomQWidgetBase):
    def __init__(self, parent=None, arduino_interface=None):
        super().__init__(parent)
        self.arduino_interface = arduino_interface
        
        self.title_label = QLabel("User Input Message", self)
        self.title_label.setAlignment(Qt.AlignCenter)  # Use Qt.AlignCenter for alignment
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        # Create Text Input Field
        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText("Enter your message here...")
        self.text_input.setStyleSheet("background-color: white; color: black; border: 2px solid blue;")
        
        # Create Submit Button
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.setEnabled(False)  # Disable the button initially
        self.submit_button.clicked.connect(self.submit_message)

        # Connect the textChanged signal to the method that updates the button state
        self.text_input.textChanged.connect(self.check_input)

        # Layout Setup
        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.text_input)
        layout.addWidget(self.submit_button)
        
        self.setLayout(layout)
        self.setMinimumSize(300, 150)

        self.addSourceKey("payload_input_message", str, Constants.payload_user_input_message_key, default_value="", hide_in_drop_down=True)

    def submit_message(self):
        user_message = self.text_input.text()
        print(user_message)
        if self.arduino_interface:
            if user_message:
                self.arduino_interface.write_arduino_data(user_message)  # Data Transmission ON, send 'b'
        self.text_input.clear()  # Clear the text input after submission

    def update_data(self, message):
        self.updated_data_dictionary['payload_input_message'] = message  # Store the message in the dictionary

    def check_input(self):
        # Check if the input text is empty and enable/disable the button accordingly
        if self.text_input.text():
            self.submit_button.setEnabled(True)  # Enable the button if the text is not empty
        else:
            self.submit_button.setEnabled(False)  # Disable the button if the text is empty
