"""
Prop Control Widget
"""

import json
import typing
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QComboBox, QGridLayout, QLabel, QWidget, QPushButton, QCheckBox
import PyQt5.QtCore as QtCore

from src.constants import Constants
from src.Widgets import custom_q_widget_base


class PropControlWidget(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        valve_types = ["Pressurant", "Purge", "Vent", "Flow", "Drip"]
        propellant_types = ["LOX", "Kerosene"]
        valve_options = ["Open", "Closed"]

        mode_options = ["Test", "Batch", "State"]
        self.test_map_dict: dict = json.load(open("src/Assets/prop_states.json"))


        self.widget_list = []

        layout = QGridLayout()
        self.setLayout(layout)

        title_widget = QLabel()
        title_widget.setText("Prop System Control")
        title_widget.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_widget, 0, 0, 1, 6)


        override_checkbox = QCheckBox(text="Override valves?")
        layout.addWidget(override_checkbox, 1, 0, 1, 2, QtCore.Qt.AlignCenter)
        send_override = QPushButton(text="Set active elements")
        send_override.setDisabled(True)
        layout.addWidget(send_override, 1, 2, 1, 1, QtCore.Qt.AlignCenter)
        self.send_override = send_override
        override_checkbox.clicked.connect(self.overrideClicked)
        override_checkbox.setChecked(False)
        self.override_checkbox = override_checkbox
        
        self.mode_switch: typing.List[QComboBox] = []
        self.mode_pushbutton: typing.List[QPushButton] = []
        for i in range(len(mode_options)):
            column = i * 2

            mode_label = QLabel()
            mode_switch = QComboBox()
            mode_button = QPushButton()

            mode_label.setText("Current {}: ".format(mode_options[i]))
            mode_button.setText("Set {}".format(mode_options[i]))
            self.mode_switch.append(mode_switch)
            self.mode_pushbutton.append(mode_button)

            layout.addWidget(mode_label, 2, column, 1, 2)
            layout.addWidget(mode_switch, 3, column, 1, 2)
            layout.addWidget(mode_button, 4, column, 1, 2)

        self.mode_switch[0].addItems(self.test_map_dict.keys())
        self.mode_switch[0].currentTextChanged.connect(self.setBatchOpts)
        self.setBatchOpts()
        self.mode_switch[1].currentTextChanged.connect(self.setTestOpts)
        self.setTestOpts()


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
                row = j + 5

                layout.addWidget(valve_name_widget, row, column)
                layout.addWidget(valve_control_widget, row, column + 1)
                layout.addWidget(valve_state_widget, row, column + 2)

    def overrideClicked(self):
        override = self.override_checkbox.isChecked()
        self.send_override.setDisabled(not override)
        for i in range(len(self.mode_switch)):
            self.mode_switch[i].setDisabled(override)
            self.mode_pushbutton[i].setDisabled(override)

    def setBatchOpts(self):
        key = self.mode_switch[0].currentText()
        self.mode_switch[1].clear()
        self.mode_switch[1].addItems(self.test_map_dict[key]) # Adds "KERO_FILL", "PURGE", etc

    def setTestOpts(self):
        batchkey = self.mode_switch[0].currentText()
        testkey = self.mode_switch[1].currentText()
        self.mode_switch[2].clear()
        self.mode_switch[2].addItems(self.test_map_dict[batchkey][testkey]) # Adds the actual states

    def updateData(self, vehicle_data, updated_data):
        pass

    def callPropCommand(self, command):
        self.callbackEvents.append([Constants.prop_command_key, command])
