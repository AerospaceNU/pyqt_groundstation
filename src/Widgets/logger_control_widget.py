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
    QTextEdit,
    QWidget,
)

from src.config import ConfigSaver
from src.constants import Constants
from src.CustomLogging.dpf_logger import DpfLogger, set_test_name
from src.data_helpers import get_value_from_dictionary
from src.Widgets import custom_q_widget_base


class LoggerControlWidget(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        layout = QGridLayout()
        self.setLayout(layout)

        title_widget = QLabel()
        title_widget.setText("Logger Control")
        title_widget.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_widget, 0, 0, 1, 3)

        layout.addWidget(QLabel(text="Test Name"), 1, 0, 1, 1)
        self.textedit = QTextEdit()
        self.textedit.setText(ConfigSaver.get("logging", "testname", "UNKNOWN"))
        self.textedit.setMaximumHeight(40)
        layout.addWidget(self.textedit, 1, 1, 1, 1)

        confirm = QPushButton(text="Set Test")
        confirm.clicked.connect(self.onClick)
        layout.addWidget(confirm, 1, 2, 1, 1)

    def onClick(self):
        testName = self.textedit.toPlainText()
        ConfigSaver.save("logging", "testname", testName)
        set_test_name(testName)
