from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.Widgets.custom_q_widget_base import CustomQWidgetBase

class PayloadTemperatureWidget(CustomQWidgetBase):
    def __init__(self, parent=None, default_temperature=20):
        super().__init__(parent)

        self.temperature_value = QLabel(f"{default_temperature}°C", self)
        self.temperature_header = QLabel("Payload Temperature", self)

        temperature_font = QFont()
        temperature_font.setPointSize(50)
        label_font = QFont()
        label_font.setPointSize(30)
        self.temperature_value.setFont(temperature_font)
        self.temperature_header.setFont(label_font) # not changing fonts whyyyyyyy

        self.temperature_value.setAlignment(Qt.AlignCenter)
        self.temperature_header.setAlignment(Qt.AlignHCenter)

        layout = QVBoxLayout(self)

        layout.addWidget(self.temperature_header)

        layout.addStretch(1)

        layout.addWidget(self.temperature_value)

        layout.addStretch(1)

        layout.setAlignment(Qt.AlignHCenter)  
        self.setLayout(layout)

        self.setMinimumSize(150, 150)

        self.update_temperature(default_temperature)

    def update_temperature(self, temperature):
        self.temperature_value.setText(f"{temperature}°C")

    def set_default_value(self, temperature):
        self.update_temperature(temperature)
