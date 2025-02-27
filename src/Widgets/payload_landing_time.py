from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLCDNumber
from src.Widgets.QWidget_Parts import simple_bar_graph_widget
from src.Widgets.custom_q_widget_base import CustomQWidgetBase
from src.constants import Constants
from PyQt5.QtCore import QTime, Qt

class PayloadLandingTimeWidget(CustomQWidgetBase):
    def __init__(self, parent=None, default_time=0):
        super().__init__(parent)
        
        # Create LCD Display
        self.lcd = QLCDNumber(self)
        self.lcd.setDigitCount(8)  # Display HH:MM:SS
        self.lcd.setStyleSheet("background-color: white; color: green; border: 2px solid green;")
        # self.lcd.setAlignment(Qt.AlignCenter)  # Center the text


        layout = QVBoxLayout()
        layout.addWidget(self.lcd)
        
        self.setLayout(layout)
        self.setMinimumSize(200,200)

        self.addSourceKey("payload_landing_time", float, Constants.payload_landing_time_key, default_value=0, hide_in_drop_down=True)

    def updateData(self, vehicle_data, updated_data):
        landing_time = self.getDictValueUsingSourceKey("payload_landing_time")
        formatted_time = QTime(0,0).addSecs(int(landing_time)).toString("H:MM:SS")
        print("TIMEEEEE", {formatted_time})
        self.lcd.display(formatted_time)

# constants, random data, ardunino, diagnostics