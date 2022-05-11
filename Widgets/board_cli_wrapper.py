"""
Text box widget
"""
from re import template
from PyQt5 import QtCore
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QListView, QListWidget, QListWidgetItem, QPushButton, QLineEdit, QLabel, QGridLayout, QTableWidget, QTableWidgetItem

import time

from Widgets import custom_q_widget_base
from data_helpers import get_qcolor_from_string

class BoardCliWrapper(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent=None):
        super().__init__(parent)


        layout = QVBoxLayout()
        self.vbox = layout
        
        self.widgetList = []

        # self.source = Constants.cli_interface_key
        self.titleBox = QLabel()
        self.title = "FCB CLI GUI"
        self.titleBox.setText(self.title)
        self.titleBox.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        layout.addWidget(self.titleBox)

        # Buttons we want to support:
        # Offload (a list of flight numbers, if they did/didn't launch, timestamp, you select one) then click the button
        # Pyro config (should be a list of MAX_PYRO many pyros, each pyro should show next to it what it's currently configured for)
        # Erase flash (with a bar showing % full beside it)

        # --- OFFLOAD ---
        self.add(QPushButton(text="Refresh data"), onClick=self.refreshData)

        self.offloadTableWidget = QTableWidget()
        self.offloadTableWidget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.offloadTableWidget.setMinimumWidth(450)

        # Eventually this needs to be dynamically recreated based on a binary message we get over USB
        self.offloadTableWidget.setRowCount(5)
        self.offloadTableWidget.setColumnCount(3)
        self.offloadTableWidget.setColumnWidth(0, 160)
        self.offloadTableWidget.setColumnWidth(1, 100)
        self.offloadTableWidget.setColumnWidth(2, 90)
        self.offloadTableWidget.setHorizontalHeaderLabels(["Date", "Duration", "Launched"])
        for i in range(5):
            # item = QTableWidgetItem(f"{i}: {'(Yes) ' if i % 2 == 0 else '(No)  '}{time.strftime('%Y-%m-%d %H:%M:%S')} for 00:01:24")
            self.offloadTableWidget.setItem(i, 0, QTableWidgetItem(time.strftime('%Y-%m-%d %H:%M:%S')))
            self.offloadTableWidget.setItem(i, 1, QTableWidgetItem("00:01:24"))
            self.offloadTableWidget.setItem(i, 2, QTableWidgetItem('Ye' if i % 2 == 0 else 'Ni'))
            # item.setBackground(get_qcolor_from_string("rgb(100,0,0)" if i % 2 == 0 else "rgb(0,100,0)"))

            for j in range(3):
                self.offloadTableWidget.item(i, j).setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)


        layout.addWidget(self.offloadTableWidget)

        tempLayout = QHBoxLayout()
        self.add(QLabel(text="Flight name: "), layout=tempLayout)
        self.offloadNameEntry = QLineEdit()
        tempLayout.addWidget(self.offloadNameEntry)
        layout.addItem(tempLayout)

        self.add(QPushButton(text="Download selected flight"), onClick=self.onOffloadSelect)
        
        """
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
        """

        self.setLayout(layout)

    def add(self, widget, layout=None, onClick=None):
        if layout is None:
            layout = self.vbox
        self.widgetList.append(widget)
        layout.addWidget(widget)

        if onClick:
            widget.clicked.connect(onClick)
            

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
        index = self.getIndexFrom(self.offloadTableWidget)

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
        self.offloadTableWidget.setStyleSheet("QHeaderView::section { background-color:rgb(13,17,23);color:rgb(255,255,255); } "
            + widget_background_string + header_text_string)
        self.offloadNameEntry.setStyleSheet(widget_background_string + header_text_string)

        for i in range(self.offloadTableWidget.rowCount()):
            for j in range(self.offloadTableWidget.columnCount()):
                self.offloadTableWidget.item(i,j).setForeground(get_qcolor_from_string(text_string))

        for widget in self.widgetList:
            widget.setStyleSheet(widget_background_string + header_text_string)

        print(widget_background_string)
        print(header_text_string)
        print(text_string)
        print(header_text_string)
