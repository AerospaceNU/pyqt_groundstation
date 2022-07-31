"""
Prop Sequencer Widget
Shows the current sequence and abort status
"""

import json
import typing
from os import abort

import PyQt5.QtCore as QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from src.constants import Constants
from src.data_helpers import get_value_from_dictionary
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

        layout.addWidget(QLabel(text="Set Sequence:"), 1, 0, 1, 1)
        self.sequence_dropdown = QComboBox()
        self.sequence_dropdown.addItems(self.test_map_dict["sequences"])
        layout.addWidget(self.sequence_dropdown, 1, 1, 1, 1)
        sequence_button = QPushButton(text="Set Sequence")
        layout.addWidget(sequence_button, 1, 2, 1, 1)
        self.abort_button = QPushButton(text="Abort Sequece")
        layout.addWidget(self.abort_button, 2, 0, 1, 3)

        sequence_button.clicked.connect(self.setSequenceClicked)
        self.abort_button.clicked.connect(self.abortClicked)

    def abortClicked(self):
        payload = {"command": "ABORT_SEQUENCE"}
        self.callPropCommand(json.dumps(payload))

    def setSequenceClicked(self):
        payload = {"command": "START_SEQUENCE", "sequence": self.sequence_dropdown.currentText()}
        self.callPropCommand(json.dumps(payload))

    def callPropCommand(self, command):
        self.callbackEvents.append([Constants.prop_command_key, command])

    # def customUpdateAfterThemeSet(self):
    #     self.abort_button.setStyleSheet(self.abort_button.styleSheet() + " background-color:red")
