"""
CLI Console
"""

from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QKeyEvent
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit, QScrollArea

from src.constants import Constants
from src.data_helpers import get_value_from_dictionary
from src.Widgets import custom_q_widget_base


class CompleteConsoleWidget(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent=None, rx_source=Constants.new_cli_message_key, tx_source=Constants.cli_interface_key):
        super().__init__(parent)

        self.textBoxWidget = QLabel()
        self.textEntryWidget = QLineEdit()
        self.titleBox = QLabel()
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.textBoxWidget)

        layout = QGridLayout()
        layout.addWidget(self.titleBox, 0, 0)
        layout.addWidget(self.scrollArea, 1, 0)
        layout.addWidget(self.textEntryWidget, 2, 0)
        self.setLayout(layout)

        self.textEntryWidget.returnPressed.connect(self.returnPressed)

        self.oldKeyPress = self.textEntryWidget.keyPressEvent  # We want to use the old key press, but do our code first
        self.textEntryWidget.keyPressEvent = self.textEntryKeyPressEvent

        self.xBuffer = 0
        self.yBuffer = 0

        self.title = "FCB CLI Interface"
        self.source = tx_source

        self.callback_handler.addCallback(rx_source, self.onCliMessage)

        self.consoleData = []

        self.titleBox.setText(self.title)
        self.titleBox.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.textBoxWidget.setFont(QFont("monospace", 10))

        # self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.setMinimumHeight(100)

        self.commandHistory = []
        self.commandHistoryIndex = -1
        self.currentCommand = ""

    def onCliMessage(self, message):
        self.consoleData.append(message)

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
        self.callback_handler.requestCallback(self.source, text)

        if len(self.commandHistory) == 0:
            self.commandHistory = [text]
        if self.commandHistory[0] != text:
            self.commandHistory = [text] + self.commandHistory

        self.currentCommand = ""
        self.commandHistoryIndex = -1

    def updateData(self, vehicle_data, updated_data):
        # data = get_value_from_dictionary(vehicle_data, self.source, [])

        at_bottom = False
        if self.scrollArea.verticalScrollBar().sliderPosition() == self.scrollArea.verticalScrollBar().maximum():
            at_bottom = True

        outString = ""
        for line in self.consoleData:
            outString = outString + line
            if outString[-1] != "\n":
                outString += "\n"

        self.textBoxWidget.setText(outString[:-1])
        self.textBoxWidget.adjustSize()
        self.adjustSize()

        self.scrollArea.setMinimumWidth(min(self.textBoxWidget.width() + 10, 1000))
        self.scrollArea.setMinimumHeight(min(self.textBoxWidget.height(), 500))

        # Fix the scroll bar after changing all the sizes
        if at_bottom:
            self.scrollArea.verticalScrollBar().setSliderPosition(self.scrollArea.verticalScrollBar().maximum())

    def customUpdateAfterThemeSet(self):
        self.textBoxWidget.setStyleSheet("font: 10pt Monospace")


class CLIUSBInterface(CompleteConsoleWidget):
    def __init__(self, parent=None):
        """
        Overrides the other console to provide the USB interface
        I'm not sure this is a great way to do this, but it'll work for now
        """
        super(CLIUSBInterface, self).__init__(parent=parent, tx_source=Constants.cli_interface_usb_key, rx_source=Constants.new_usb_cli_message_key)

        self.title = "FCB CLI USB Interface"

        self.titleBox.setText(self.title)
