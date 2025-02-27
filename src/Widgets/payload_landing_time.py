from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLCDNumber
from src.Widgets.QWidget_Parts import simple_bar_graph_widget
from src.Widgets.custom_q_widget_base import CustomQWidgetBase
from src.constants import Constants

class PayloadLandingTimeWidget(CustomQWidgetBase):
    def __init__(self, parent=None, default_time=0):
        super().__init__(parent)
        
        # Create LCD Display
        self.lcd = QLCDNumber(self)
        self.lcd.setDigitCount(default_time)  # Display HH:MM:SS
        self.lcd.setStyleSheet("background-color: black; color: green; border: 2px solid green;")

        layout = QVBoxLayout()
        layout.addWidget(self.lcd)
        
        self.setLayout(layout)
        self.setMinimumSize(200,200)

        self.addSourceKey("payload_time", float, Constants.payload_landing_time_key, default_value=0, hide_in_drop_down=True)

    def update_time(self):
        landing_time = self.getDictValueUsingSourceKey("payload_time")
        self.lcd.display(landing_time)

# constants, random data, ardunino, diagnostics