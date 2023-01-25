"""
Widget to show filght events over radio
"""

from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QKeyEvent
from PyQt5.QtWidgets import QGridLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem

from src.constants import Constants
from src.data_helpers import get_value_from_dictionary
from src.Widgets import custom_q_widget_base

REQUEST_EVENT_COMMAND = "--config -h"


class EventConfiguration(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.titleBox = QLabel()
        self.reloadButton = QPushButton()
        self.sendDataButton = QPushButton()
        self.tableWidget = QTableWidget()

        layout = QGridLayout()
        layout.addWidget(self.titleBox, 0, 0, 0, 2)
        layout.addWidget(self.reloadButton, 0, 0, 1, 1)
        layout.addWidget(self.sendDataButton, 0, 1, 1, 1)
        layout.addWidget(self.tableWidget, 2, 0, 1, 2)
        self.setLayout(layout)

        self.reloadButton.setText("Refresh")
        self.sendDataButton.setText("Set Configuration")

        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(0)
        # self.tableWidget.setMinimumWidth(450)
        # self.tableWidget.setMinimumHeight(600)
        self.tableWidget.setHorizontalHeaderLabels(["Event", "Description"])

        self.reloadButton.clicked.connect(self.onRefreshButton)

        self.callback_handler.addCallback(Constants.new_cli_message_key, self.onCliMessage)

        self.isGettingEventData = False
        self.waitingForDataStart = False

    def onRefreshButton(self):
        self.callback_handler.requestCallback(Constants.cli_interface_key, REQUEST_EVENT_COMMAND)

    def onCliMessage(self, message: str):
        message = message.strip().lstrip("0123456789:").strip()  # Remove leading timestamp
        if len(message) == 0:
            return

        if REQUEST_EVENT_COMMAND in message:
            self.waitingForDataStart = True

        if self.waitingForDataStart and "OK" in message:
            self.isGettingEventData = True
            self.waitingForDataStart = False
            self.resetConfig()
            return

        if self.isGettingEventData:
            if "DONE" in message:
                self.isGettingEventData = False
            else:
                self.newConfigLine(message)

    def resetConfig(self):
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)

    def newConfigLine(self, line):
        parts = line.split(":   ")
        parts = [part.strip() for part in parts]

        self.addToTable(parts)

    def addToTable(self, parts):
        row_index = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_index)

        self.tableWidget.setItem(row_index, 0, QTableWidgetItem(parts[0]))
        self.tableWidget.setItem(row_index, 1, QTableWidgetItem(parts[1]))
        self.tableWidget.adjustSize()
        self.adjustSize()

    def updateData(self, vehicle_data, updated_data):
        pass
