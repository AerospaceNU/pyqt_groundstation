"""
Text box widget
"""
from re import template
from PyQt5 import QtCore
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QListView, QListWidget, QListWidgetItem, QPushButton, QLineEdit, QLabel, QGridLayout, QTableWidget, QTableWidgetItem

import time

from Widgets import custom_q_widget_base
from data_helpers import get_qcolor_from_string, get_well_formatted_rgb_string


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
        self.offloadTableWidget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.offloadTableWidget.setMinimumWidth(450)
        self.offloadTableWidget.setColumnCount(3)
        self.offloadTableWidget.setColumnWidth(0, 160)
        self.offloadTableWidget.setColumnWidth(1, 100)
        self.offloadTableWidget.setColumnWidth(2, 90)
        self.offloadTableWidget.setHorizontalHeaderLabels(["Date", "Duration", "Launched"])
        layout.addWidget(self.offloadTableWidget)

        self.recreate_table("")

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

    def recreate_table(self, offload_help_string):
        flight_array = self.parseOffloadHelp(offload_help_string)
        self.offloadTableWidget.setRowCount(max(map(lambda row: int(row[0]), flight_array)) + 1)
        for i in range(len(flight_array)):
            row = flight_array[i]
            row_num = int(row[0])
            self.offloadTableWidget.setItem(row_num, 0, QTableWidgetItem(row[2]))
            self.offloadTableWidget.setItem(row_num, 1, QTableWidgetItem(row[3]))
            self.offloadTableWidget.setItem(row_num, 2, QTableWidgetItem(row[1]))
            # item.setBackground(get_qcolor_from_string("rgb(100,0,0)" if i % 2 == 0 else "rgb(0,100,0)"))

            for j in range(3):
                item = self.offloadTableWidget.item(row_num, j)
                if item is not None:
                    item.setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)


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
        if (len(indexes) < 1):
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
        background_color_string = get_well_formatted_rgb_string(widget_background_string.split(":")[1].strip())
        text_color_string = get_well_formatted_rgb_string(text_string.split(":")[1].strip())

        header_section_string = "QHeaderView::section { background-color:" + background_color_string + "; color:" + text_color_string + ";} "
        corner_section_string = "QTableCornerButton::section {background-color: " + background_color_string + "; }"

        self.setStyleSheet("QWidget#" + self.objectName() + " {" + border_string + widget_background_string + text_string + "}")
        self.titleBox.setStyleSheet(widget_background_string + header_text_string)
        self.offloadTableWidget.setStyleSheet(header_section_string + " " + corner_section_string)
        self.offloadNameEntry.setStyleSheet(widget_background_string + header_text_string + border_string)

        for i in range(self.offloadTableWidget.rowCount()):
            for j in range(self.offloadTableWidget.columnCount()):
                item = self.offloadTableWidget.item(i, j)
                if item is not None:
                    item.setForeground(get_qcolor_from_string(text_string))
                    item.setBackground(get_qcolor_from_string(widget_background_string))

        for widget in self.widgetList:
            widget.setStyleSheet(widget_background_string + header_text_string)

    def parseOffloadHelp(self, cli_string: str):
        cli_str = "\r\nOK\r\nAvailable flights to offload:\r\nLast: 10      Last launched: 9\r\n"\
            + "| Fight # | Launched | Timestamp | Flight Duration |\r\n"\
            + "| 0 | true | None | 00:00:13 |\r\n"\
            + "| 1 | true | Mon Feb  7 02:38:37 2022 | 00:02:10 |\r\n"\
            + "| 3 | false | Mon Jan  2 02:38:37     2020 | 00:10:33 |\r\n"\
            + "\r\n\r\nDONE\r\n"

        # Filter for lines that start with | and split by return characters
        cli_str = list(filter(lambda line : line.startswith("|"), cli_str.splitlines()))
        # And only return ones with a numeric flight number
        twoDarray = [list(map(lambda s : s.strip(), line.split("|")[1:-1])) for line in cli_str if line.split("|")[1].strip().isnumeric()]

        return twoDarray

