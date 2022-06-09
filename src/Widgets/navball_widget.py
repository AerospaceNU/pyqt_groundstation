"""
Widget for buttons
"""

from PyQt5.QtWidgets import QGridLayout, QWidget

from src.constants import Constants
from src.data_helpers import get_value_from_dictionary
from src.Widgets import custom_q_widget_base
from src.Widgets.QWidget_Parts.navball_display_widget import NavballDisplayWidget


class NavballWidget(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.navballDisplayWidget = NavballDisplayWidget()

        layout = QGridLayout()
        layout.addWidget(self.navballDisplayWidget)
        layout.setContentsMargins(1, 1, 1, 1)
        self.setLayout(layout)

    def updateData(self, vehicle_data, updated_data):
        orientation = get_value_from_dictionary(vehicle_data, Constants.orientation_quaternion_key, None)
        if orientation is not None:
            self.navballDisplayWidget.setOrientation(orientation)
        else:
            roll = get_value_from_dictionary(vehicle_data, Constants.roll_position_key, 0)
            pitch = get_value_from_dictionary(vehicle_data, Constants.pitch_position_key, 0)
            yaw = get_value_from_dictionary(vehicle_data, Constants.yaw_position_key, 0)
            self.navballDisplayWidget.setRPY(roll, pitch, yaw)

    def updateInFocus(self):
        self.navballDisplayWidget.update()  # Re-render navball
