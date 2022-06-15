"""
Prop Control Widget
"""

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QComboBox, QGridLayout, QLabel, QWidget, QPushButton

from src.constants import Constants
from src.Widgets import custom_q_widget_base


class PropControlWidget(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        valve_types = ["Pressurant", "Purge", "Vent", "Flow", "Drip"]
        propellant_types = ["LOX", "Kerosene"]
        valve_options = ["Open", "Closed"]

        mode_options = ["Test", "Batch", "State"]

        self.widget_list = []

        layout = QGridLayout()
        self.setLayout(layout)

        title_widget = QLabel()
        title_widget.setText("Prop System Control")
        layout.addWidget(title_widget, 0, 0, 1, 6)

        for i in range(len(mode_options)):
            column = i * 2

            mode_label = QLabel()
            mode_switch = QComboBox()
            mode_button = QPushButton()

            mode_label.setText("Current {}: ".format(mode_options[i]))
            mode_button.setText("Set {}".format(mode_options[i]))

            layout.addWidget(mode_label, 1, column, 1, 2)
            layout.addWidget(mode_switch, 2, column, 1, 2)
            layout.addWidget(mode_button, 3, column, 1, 2)

        for i in range(len(propellant_types)):
            propellant_name = propellant_types[i]
            for j in range(len(valve_types)):
                valve_name = valve_types[j]

                valve_name_widget = QLabel()
                valve_control_widget = QComboBox()
                valve_state_widget = QLabel()

                valve_name_widget.setText("{0} {1}".format(propellant_name, valve_name))
                valve_control_widget.addItems(valve_options)
                valve_state_widget.setText("Unknown")

                column = 3 * i
                row = j + 4

                layout.addWidget(valve_name_widget, row, column)
                layout.addWidget(valve_control_widget, row, column + 1)
                layout.addWidget(valve_state_widget, row, column + 2)

    def updateData(self, vehicle_data, updated_data):
        pass

    def callPropCommand(self, command):
        self.callbackEvents.append([Constants.prop_command_key, command])
