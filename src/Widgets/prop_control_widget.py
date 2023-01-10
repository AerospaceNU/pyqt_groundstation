"""
Prop Control Widget
"""

import json
import typing

import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from src.constants import Constants
from src.data_helpers import get_value_from_dictionary
from src.Widgets import custom_q_widget_base


def make_lambda(callback, arg):
    return lambda: callback(arg)


class PropControlWidget(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        # Row defines
        STATE_ROW = 3

        MODE_LABEL_ROW = 4
        MODE_SWITCH_ROW = 5
        STATE_BUTTON_ROW = 6
        HOTBUTTON_HBOX_ROW = 7
        VALVE_DISPLAY_START = 8

        valve_types = ["Pressurant", "Purge", "Vent", "Flow"]
        propellant_types = ["LOX", "Kerosene"]
        valve_options = ["OPEN", "CLOSED"]

        mode_options = ["Test", "Batch", "State"]
        self.mode_options = mode_options
        self.test_map_dict: dict = json.load(open("src/Assets/prop_states.json"))

        layout = QGridLayout()
        self.setLayout(layout)
        layout.setVerticalSpacing(15)

        title_widget = QLabel()
        title_widget.setText("            Prop System Control")
        title_widget.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_widget, 0, 2, 1, 2)

        override_checkbox = QCheckBox(text="Override valves?")
        layout.addWidget(override_checkbox, 1, 1, 1, 3, QtCore.Qt.AlignCenter)
        send_override = QPushButton(text="Set active elements")
        send_override.setDisabled(True)
        send_override.clicked.connect(self.sendOverrideClicked)
        layout.addWidget(send_override, 1, 3, 1, 3, QtCore.Qt.AlignLeft)
        self.send_override = send_override
        self.override_checkbox = override_checkbox
        override_checkbox.clicked.connect(self.overrideClicked)
        override_checkbox.setChecked(False)

        # Current state/sequence display, wrapped in a widget to make borders
        statedisplaywidget = QFrame(self)
        row = QGridLayout()
        statedisplaywidget.setLayout(row)
        statelabellabel = QLabel(text="Current state:")
        self.state_label = QLabel(text="Foobar")
        row.addWidget(statelabellabel, 0, 0, 1, 1)
        row.addWidget(self.state_label, 0, 1, 1, 2)
        sequencelabellabel = QLabel(text="Current sequence:")
        self.sequence_label = QLabel(text="Foobar")
        row.addWidget(sequencelabellabel, 0, 3, 1, 1)
        row.addWidget(self.sequence_label, 0, 4, 1, 2)
        abortlabellabel = QLabel(text="Last abort:")
        self.abort_label = QLabel(text="Foobar")
        row.addWidget(abortlabellabel, 0, 6, 1, 1)
        row.addWidget(self.abort_label, 0, 7, 1, 2)
        layout.addWidget(statedisplaywidget, STATE_ROW, 0, 1, 6)

        # topsplit = QSplitter(QtCore.Qt.Horizontal)
        # bottomsplitter = QSplitter(QtCore.Qt.Horizontal)
        # layout.addWidget(topsplit, STATE_ROW-1, 0, 1, 6)
        # layout.addWidget(bottomsplitter, STATE_ROW+1, 0, 1, 6)
        # self.splitters = [topsplit, bottomsplitter]

        self.mode_switch: typing.List[QComboBox] = []
        self.mode_pushbutton: QPushButton = []
        for i in range(len(mode_options)):
            column = i * 2

            mode_label = QLabel()
            mode_switch = QComboBox()

            mode_label.setText("Current {}: ".format(mode_options[i]))
            self.mode_switch.append(mode_switch)

            layout.addWidget(mode_label, MODE_LABEL_ROW, column, 1, 2)
            layout.addWidget(mode_switch, MODE_SWITCH_ROW, column, 1, 2)

        # layout.setSpacing(15)

        # Just button to set state, it's gunna look whack but that's OK
        mode_button = QPushButton()
        # mode_button.setGeometry(30, 300, 700, 40)
        mode_button.setText("Set State")
        self.mode_pushbutton = mode_button
        layout.addWidget(mode_button, STATE_BUTTON_ROW, 0, 1, 6)

        # QFrame to hold the hot buttons
        hotbuttonFrame = QFrame()
        layout.addWidget(hotbuttonFrame, HOTBUTTON_HBOX_ROW, 0, 1, 6)
        hotbuttonhbox = QHBoxLayout()
        hotbuttonFrame.setLayout(hotbuttonhbox)
        self.hot_buttons = []

        hotbutton_allowed = QCheckBox(text="Allow hotbuttons")
        hotbuttonhbox.addWidget(hotbutton_allowed)
        # Add horizontal spacing around hotbuttons
        hotbuttonhbox.setSpacing(50)
        hotbutton_allowed.clicked.connect(lambda: [s.setDisabled(not hotbutton_allowed.isChecked()) for s in self.hot_buttons])
        hotbutton_allowed.setChecked(False)

        hotbuttons = json.load(open("src/Assets/prop_hotbuttons.json"))
        for category in hotbuttons:
            for buttonText in hotbuttons[category]:
                button = QPushButton(text=buttonText)
                # TODO hook button press up
                hotbuttonhbox.addWidget(button)
                self.hot_buttons.append(button)
                button.setDisabled(True)

                # Python lambda closures are dumb, so we need to use make_lambda or the lambda is bound
                # to whatever the last button we clicked is.
                if category == "sequences":
                    button.clicked.connect(make_lambda(self.setSequenceFromString, buttonText))
                    if buttonText == "PURGE_ABORT":
                        button.setProperty("class", "danger")
                else:  # state
                    button.clicked.connect(make_lambda(self.setStateFromString, buttonText))

        # Add some vertical padding above/below hotbuttons
        hotbuttonFrame.setMinimumHeight(hotbuttonhbox.sizeHint().height() + 30)

        # Min width for State column
        layout.setColumnMinimumWidth(2 * 2, 140)

        self.mode_switch[0].addItems(self.test_map_dict.keys())
        # Set the current test dropdown to the last saved, or zero by default
        self.mode_switch[0].setCurrentIndex(self.widgetSettings.get(mode_options[0], 0, type=int))
        self.mode_switch[0].currentTextChanged.connect(self.setBatchOpts)

        # Load the batch dropdown based on current test
        self.setBatchOpts()

        # Set the current batch dropdown to the last saved, or zero by default
        self.mode_switch[1].setCurrentIndex(self.widgetSettings.get(mode_options[1], 0, type=int))

        self.mode_switch[1].currentTextChanged.connect(self.setTestOpts)
        self.setTestOpts()
        self.mode_pushbutton.clicked.connect(self.setState)

        # Set the state dropdown based on last saved
        self.mode_switch[2].setCurrentIndex(self.widgetSettings.get(mode_options[2], 0, type=int))
        self.mode_switch[2].currentTextChanged.connect(lambda: self.widgetSettings.save(self.mode_options[2], self.mode_switch[2].currentIndex()))

        self.prop_comboboxes: typing.Dict[QComboBox] = {}
        self.valve_state_boxes: typing.Dict[QLabel] = {}

        for i in range(len(propellant_types)):
            propellant_name = propellant_types[i]
            for j in range(len(valve_types)):
                valve_type = valve_types[j]
                valve_name_text = "{0} {1}".format(propellant_name, valve_type)
                valve_name = propellant_name.lower()[0:3] + valve_type

                valve_name_widget = QLabel()
                valve_control_widget = QComboBox()
                valve_state_widget = QLabel()
                self.prop_comboboxes[valve_name] = valve_control_widget
                self.valve_state_boxes[valve_name] = valve_state_widget

                valve_state_widget.text

                valve_name_widget.setText(valve_name_text)
                valve_control_widget.addItems(valve_options)
                valve_state_widget.setText("Unknown")

                column = 3 * i
                row = j + VALVE_DISPLAY_START

                layout.addWidget(valve_name_widget, row, column)
                layout.addWidget(valve_control_widget, row, column + 1)
                layout.addWidget(valve_state_widget, row, column + 2)

        # Last so we can set state
        self.overrideClicked()

    def overrideClicked(self):
        override = self.override_checkbox.isChecked()
        self.send_override.setDisabled(not override)
        for i in range(len(self.mode_switch)):
            self.mode_switch[i].setDisabled(override)

        self.mode_pushbutton.setDisabled(override)

        for combo in self.prop_comboboxes:
            self.prop_comboboxes[combo].setDisabled(not override)

        if override:
            # Set all override dropdowns to current valve states
            for valve_name in self.prop_comboboxes:
                # Coboboxes = the dropdown you select desired state from
                # state_boxes = label showing current state
                self.prop_comboboxes[valve_name].setCurrentText(self.valve_state_boxes[valve_name].text())

    def setBatchOpts(self):
        # Batch dropdown just changed, so save it
        self.widgetSettings.save(self.mode_options[0], self.mode_switch[0].currentIndex())

        key = self.mode_switch[0].currentText()
        self.mode_switch[1].clear()
        self.mode_switch[1].addItems(self.test_map_dict[key])  # Adds "KERO_FILL", "PURGE", etc

    def setTestOpts(self):
        # Test dropdown just changed, so save it
        self.widgetSettings.save(self.mode_options[1], self.mode_switch[1].currentIndex())

        batch_key = self.mode_switch[0].currentText()
        test_key = self.mode_switch[1].currentText()
        if len(test_key) > 0 and len(batch_key) > 0:
            self.mode_switch[2].clear()
            self.mode_switch[2].addItems(self.test_map_dict[batch_key][test_key])  # Adds the actual states

    def sendOverrideClicked(self):
        active_elements = {}

        for box in self.prop_comboboxes:
            active_elements[box] = self.prop_comboboxes[box].currentText().upper()

        payload = {"command": "SET_ACTIVE_ELEMENTS", "activeElements": active_elements}
        self.callPropCommand(json.dumps(payload))

    def setState(self):
        self.setStateFromString(self.mode_switch[2].currentText())

    def setStateFromString(self, state: str):
        payload = {"command": "SET_STATE", "newState": state}
        self.callPropCommand(json.dumps(payload))

    def setSequenceFromString(self, sequence: str):
        payload = {"command": "START_SEQUENCE", "sequence": sequence}
        self.callPropCommand(json.dumps(payload))

    def updateData(self, vehicle_data, updated_data):
        for valve_name in self.valve_state_boxes:
            valve_state = get_value_from_dictionary(vehicle_data, valve_name, "UNKNOWN")
            self.valve_state_boxes[valve_name].setText(valve_state)

        self.state_label.setText(get_value_from_dictionary(vehicle_data, "ecs_currentState", "UNKNOWN"))
        self.sequence_label.setText(get_value_from_dictionary(vehicle_data, "ecs_engineSequence", "UNKNOWN"))
        self.abort_label.setText(get_value_from_dictionary(vehicle_data, "ecs_recordedAbort", "UNKNOWN"))

    def callPropCommand(self, command):
        self.callback_handler.requestCallback(Constants.prop_command_key, command)


if __name__ == "__main__":

    from PyQt5.QtWidgets import QApplication, QMainWindow

    application = QApplication([])  # PyQt Application object
    mainWindow = QMainWindow()  # PyQt MainWindow widget

    navball = PropControlWidget()
    navball.customUpdateAfterThemeSet()

    # navball.yaw = -90
    # navball.pitch = 90

    mainWindow.setCentralWidget(navball)
    mainWindow.show()

    from qt_material import apply_stylesheet

    apply_stylesheet(application, theme="themes/old_dark_mode.xml")

    application.exec_()
