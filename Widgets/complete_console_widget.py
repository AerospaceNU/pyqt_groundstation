"""
Text box widget
"""
from PyQt5 import QtCore
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QLabel, QGridLayout, QLineEdit
from PyQt5.QtGui import QKeyEvent, QFont

from data_helpers import get_value_from_dictionary
from constants import Constants

from Widgets import custom_q_widget_base


class CompleteConsoleWidget(custom_q_widget_base.CustomQWidgetBase):
    i = 0.0

    def __init__(self, parent=None):
        super().__init__(parent)

        self.textBoxWidget = QLabel()
        self.textEntryWidget = QLineEdit()
        self.titleBox = QLabel()

        layout = QGridLayout()
        layout.addWidget(self.titleBox)
        layout.addWidget(self.textBoxWidget)
        layout.addWidget(self.textEntryWidget)
        self.setLayout(layout)

        self.textEntryWidget.returnPressed.connect(self.returnPressed)

        self.oldKeyPress = self.textEntryWidget.keyPressEvent  # We want to use the old key press, but do our code first
        self.textEntryWidget.keyPressEvent = self.textEntryKeyPressEvent

        self.xBuffer = 0
        self.yBuffer = 0

        self.source = Constants.cli_interface_key
        self.title = "FCB CLI Interface"

        self.titleBox.setText(self.title)
        self.titleBox.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.textBoxWidget.setFont(QFont("monospace", 10))

        self.commandHistory = []
        self.commandHistoryIndex = -1
        self.currentCommand = ""

    def textEntryKeyPressEvent(self, eventQKeyEvent: QKeyEvent):
        if eventQKeyEvent.key() == 16777235:  # UP
            if self.commandHistoryIndex == -1:  # If we're editing the newest command
                self.currentCommand = self.textEntryWidget.text()
            if len(self.commandHistory) > 0:
                self.commandHistoryIndex = min(len(self.commandHistory) - 1, self.commandHistoryIndex + 1)
                self.textEntryWidget.setText(self.commandHistory[self.commandHistoryIndex])
        elif eventQKeyEvent.key() == 16777237:  # DOWN
            self.commandHistoryIndex = max(self.commandHistoryIndex - 1, -1)
            if self.commandHistoryIndex == -1:
                self.textEntryWidget.setText(self.currentCommand)
            else:
                self.textEntryWidget.setText(self.commandHistory[self.commandHistoryIndex])

        self.oldKeyPress(eventQKeyEvent)

    def returnPressed(self):
        text = self.textEntryWidget.text()
        if text.strip() == "":
            return

        self.textEntryWidget.clear()
        self.callbackEvents.append([self.source, text])

        if len(self.commandHistory) == 0:
            self.commandHistory = [text]
        if self.commandHistory[0] != text:
            self.commandHistory = [text] + self.commandHistory

        self.currentCommand = ""
        self.commandHistoryIndex = -1

    def updateData(self, vehicle_data, updated_data):
        data = get_value_from_dictionary(vehicle_data, self.source, [])

        outString = ""
        for line in data:
            outString = outString + line
            if outString[-1] != "\n":
                outString += "\n"

        self.textBoxWidget.setText(outString[:-1])
        self.adjustSize()

    def setWidgetColors(self, widget_background_string, text_string, header_text_string, border_string):
        self.setStyleSheet("QWidget#" + self.objectName() + " {" + border_string + widget_background_string + text_string + "}")
        self.textBoxWidget.setStyleSheet(widget_background_string + text_string)
        self.textEntryWidget.setStyleSheet(border_string + widget_background_string + text_string)
        self.titleBox.setStyleSheet(widget_background_string + header_text_string)
