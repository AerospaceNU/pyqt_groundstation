"""
Prop Sequencer Widget
Shows the current sequence and abort status
"""

import json

import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import (
    QComboBox,
    QGridLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QWidget,
)

from src.constants import Constants
from src.data_helpers import clamp, get_value_from_dictionary
from src.Widgets import custom_q_widget_base


class PropSequencerWidget(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.test_map_dict: dict = json.load(open("src/Assets/prop_sequences.json"))

        layout = QGridLayout()
        self.setLayout(layout)

        title_widget = QLabel()
        title_widget.setText("Engine Sequencer Control")
        title_widget.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_widget, 0, 0, 1, 3)

        # Need a row with Set Sequence: [ dropdown with json contents ]
        # and a big old ABORT SEQUENCE button

        layout.addWidget(QLabel(text="Set Sequence"), 1, 0, 1, 1)
        self.sequence_dropdown = QComboBox()
        self.sequence_dropdown.addItems(self.test_map_dict["sequences"])
        layout.addWidget(self.sequence_dropdown, 1, 1, 1, 2)
        sequence_button = QPushButton(text="Set Sequence")
        layout.addWidget(sequence_button, 2, 0, 1, 3)

        sequence_button.clicked.connect(self.setSequenceClicked)

        # show progress
        progresslabel = QLabel("Sequence Progress")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(progresslabel, 3, 0, 1, 1)
        layout.addWidget(self.progress_bar, 3, 1, 1, 2)

        # Abort button after a spacer
        layout.setVerticalSpacing(20)
        self.abort_button = QPushButton(text="Stop Sequence")
        self.abort_button.clicked.connect(self.abortClicked)
        layout.addWidget(self.abort_button, 5, 0, 1, 3)
        self.abort_button.setProperty("class", "danger")

    def abortClicked(self):
        payload = {"command": "ABORT_SEQUENCE"}
        self.callPropCommand(json.dumps(payload))

    def setSequenceClicked(self):
        payload = {"command": "START_SEQUENCE", "sequence": self.sequence_dropdown.currentText()}
        self.callPropCommand(json.dumps(payload))

    def callPropCommand(self, command):
        self.callback_handler.requestCallback(Constants.prop_command_key, command)

    def updateData(self, vehicle_data, updated_data):
        progress_percent = clamp(int(get_value_from_dictionary(vehicle_data, "ecs_sequenceProgress", 0) * 100), 0, 100)
        self.progress_bar.setValue(progress_percent)


if __name__ == "__main__":
    global i
    i = 0

    from PyQt5.QtCore import QTimer
    from PyQt5.QtWidgets import QApplication, QMainWindow

    application = QApplication([])  # PyQt Application object
    mainWindow = QMainWindow()  # PyQt MainWindow widget

    navball = PropSequencerWidget()

    # navball.yaw = -90
    # navball.pitch = 90

    mainWindow.setCentralWidget(navball)
    mainWindow.show()

    from qt_material import apply_stylesheet

    # apply_stylesheet(application, theme="themes/old_dark_mode.xml")
    apply_stylesheet(application, theme="themes/high_contrast_light.xml")
    navball.customUpdateAfterThemeSet()

    timer = QTimer()

    def timeout():
        global i
        navball.updateData({"ecs_sequenceProgress": i}, {})
        i = i + 0.02

    timer.timeout.connect(timeout)
    timer.start(50)

    application.exec_()
