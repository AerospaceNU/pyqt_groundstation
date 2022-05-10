"""
Text box widget
"""
from re import template
from PyQt5 import QtCore
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QListView, QListWidget, QListWidgetItem, QPushButton, QLineEdit, QLabel, QGridLayout

import time

from Widgets import custom_q_widget_base
from data_helpers import get_qcolor_from_string

class BoardCliWrapper(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.titleBox = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.titleBox)

        # self.source = Constants.cli_interface_key
        self.title = "FCB CLI GUI"
        self.titleBox.setText(self.title)
        self.titleBox.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

        # Buttons we want to support:
        # Offload (a list of flight numbers, if they did/didn't launch, timestamp, you select one) then click the button
        # Pyro config (should be a list of MAX_PYRO many pyros, each pyro should show next to it what it's currently configured for)
        # Erase flash (with a bar showing % full beside it)

        # --- OFFLOAD ---

        self.getDataButton = QPushButton(text="Refresh data")
        self.getDataButton.clicked.connect(self.refreshData)
        layout.addWidget(self.getDataButton)
        self.offloadListWidget = QListWidget()
        self.offloadListWidget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.offloadListWidget.setMinimumWidth(300)
        # self.offloadListWidget.setWindowTitle("(Launched) (Timestamp) (Duration)")  # Apparently this doesn't do anything

        # Eventually this needs to be dynamically recreated based on a binary message we get over USB
        self.fcbFlightsEntries = []
        for i in range(5):
            item = QListWidgetItem()
            item.setText(f"{i}: {'(Yes) ' if i % 2 == 0 else '(No)  '}{time.strftime('%Y-%m-%d %H:%M:%S')} for 00:01:24")
            # item.setBackground(get_qcolor_from_string("rgb(100,0,0)" if i % 2 == 0 else "rgb(0,100,0)"))
            self.offloadListWidget.addItem(item)
            self.fcbFlightsEntries.append(item)

        layout.addWidget(self.offloadListWidget)

        tempLayout = QHBoxLayout()
        self.label = QLabel(text="Name: ")
        self.offloadNameEntry = QLineEdit()
        tempLayout.addWidget(self.label)
        tempLayout.addWidget(self.offloadNameEntry)
        layout.addItem(tempLayout)

        self.getFlightButton = QPushButton(text="Get selected flight")
        self.getFlightButton.clicked.connect(self.onOffloadSelect)
        layout.addWidget(self.getFlightButton)
        
        # Also want a list of local flights that updates when you offload, so you can select a flight to graph
        self.localLabel = QLabel(text="Downloaded Flights")
        layout.addWidget(self.localLabel)
        self.localFlightEntries = []
        self.downloadedFlightsWidget = QListWidget()
        self.downloadedFlightsWidget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.downloadedFlightsWidget.setMinimumWidth(350)
        for i in range(5):
            item = QListWidgetItem()
            item.setText(f"User Title Here (FCBV{i % 2} #{i}, 2022:11:22 12:34:56)")
            # item.setBackground(get_qcolor_from_string("rgb(100,0,0)" if i % 2 == 0 else "rgb(0,100,0)"))
            self.downloadedFlightsWidget.addItem(item)
            self.localFlightEntries.append(item)
        layout.addWidget(self.downloadedFlightsWidget)

        # Buttons to post-process or graph
        tempLayout = QGridLayout()
        self.postProcessBtn = QPushButton(text="Post-Process Selected")
        self.postProcessBtn.clicked.connect(self.onPostProcessSelect)
        self.graphBtn = QPushButton(text="Graph Selected")
        self.graphBtn.clicked.connect(self.onGraphSelect)
        tempLayout.addWidget(self.postProcessBtn)
        tempLayout.addWidget(self.graphBtn)
        layout.addItem(tempLayout)

        self.setLayout(layout)

    def refreshData(self):
        print("Refresh data!")

    def getIndexFrom(self, listWidget):
        indexes = listWidget.selectedIndexes()
        if(len(indexes) < 1):
            return

        index = indexes[0]
        index = index.row()
        return index

    def onOffloadSelect(self):
        index = self.getIndexFrom(self.offloadListWidget)

        print(f"Index {index} clicked with name {self.offloadNameEntry.text()}")

    def onPostProcessSelect(self):
        print("Post process index " + str(self.getIndexFrom(self.downloadedFlightsWidget)))

    def onGraphSelect(self):
        print("Graph index " + str(self.getIndexFrom(self.downloadedFlightsWidget)))

    def updateData(self, vehicle_data, updated_data):
        pass

    def setWidgetColors(self, widget_background_string, text_string, header_text_string, border_string):
        self.setStyleSheet("QWidget#" + self.objectName() + " {" + border_string + widget_background_string + text_string + "}")
        self.titleBox.setStyleSheet(widget_background_string + header_text_string)
        self.offloadListWidget.setStyleSheet(widget_background_string + header_text_string)
        self.getDataButton.setStyleSheet(widget_background_string + header_text_string)
        self.getFlightButton.setStyleSheet(widget_background_string + header_text_string)
        self.offloadNameEntry.setStyleSheet(widget_background_string + header_text_string)
        self.label.setStyleSheet(widget_background_string + header_text_string)