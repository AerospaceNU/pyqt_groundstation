"""
Text box widget
"""

from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from src.constants import Constants
from src.data_helpers import get_value_from_dictionary
from src.Widgets import custom_q_widget_base
from src.Widgets.QWidget_Parts.simple_bar_graph_widget import SimpleBarGraphWidget


class BoardCliWrapper(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        self.vbox = layout
        self.command_in_progress = False

        # self.source = Constants.cli_interface_key
        self.titleBox = QLabel()
        self.title = "FCB CLI GUI"
        self.titleBox.setText(self.title)
        self.titleBox.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        layout.addWidget(self.titleBox)
        # self.callback_handler.addCallback(Constants.cli_interface_usb_result_key, self.processFcbResultCallback)

        # Buttons we want to support:
        # Offload (a list of flight numbers, if they did/didn't launch, timestamp, you select one) then click the button
        # Pyro config (should be a list of MAX_PYRO many pyros, each pyro should show next to it what it's currently configured for)
        # Erase flash (with a bar showing % full beside it)

        # --- OFFLOAD ---
        self.refreshButton = self.add(QPushButton(text="Refresh data"), onClick=self.refreshData)

        self.offloadTableWidget = QTableWidget()
        self.offloadTableWidget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.offloadTableWidget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.offloadTableWidget.setMinimumWidth(450)
        self.offloadTableWidget.setMinimumHeight(600)
        self.offloadTableWidget.setColumnCount(3)
        self.offloadTableWidget.setColumnWidth(0, 160)
        self.offloadTableWidget.setColumnWidth(1, 100)
        self.offloadTableWidget.setColumnWidth(2, 90)
        self.offloadTableWidget.setHorizontalHeaderLabels(["Date", "Duration", "Launched"])
        self.offloadTableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.offloadTableWidget)

        self.recreate_table("")

        tempLayout = QHBoxLayout()
        self.add(QLabel(text="Flight name: "), layout=tempLayout)
        self.offloadNameEntry = QLineEdit()
        tempLayout.addWidget(self.offloadNameEntry)
        layout.addItem(tempLayout)

        self.downloadButton = self.add(QPushButton(text="Download selected flight"), onClick=self.onOffloadSelect)
        self.eraseButton = self.add(QPushButton(text="Erase FCB Memory"), onClick=self.erase)

        self.addSourceKey(
            "flights_list",
            str,
            Constants.cli_flights_list_key,
            default_value="",
            hide_in_drop_down=True,
        )

        self.setLayout(layout)

    def setCommandInProgress(self, inProgress: bool):
        for w in [self.downloadButton, self.eraseButton, self.refreshButton]:
            w.setDisabled(inProgress)

    def erase(self):
        self.runPythonAvionicsCommand("erase")

    def recreate_table(self, offload_help_string):
        flight_array = self.parseOffloadHelp(offload_help_string)
        if len(flight_array) > 0:
            self.offloadTableWidget.setRowCount(max(map(lambda row: int(row[0]), flight_array)))
        else:
            self.offloadTableWidget.setRowCount(1)
        for i in range(len(flight_array)):
            row = flight_array[i]
            row_num = int(row[0]) - 1
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
        layout.addWidget(widget)

        if onClick:
            widget.clicked.connect(onClick)

        return widget

    def refreshData(self):
        self.runPythonAvionicsCommand("offload --list")

    def getIndexFrom(self, listWidget):
        indexes = listWidget.selectedIndexes()
        if len(indexes) < 1:
            return

        index = indexes[0]
        index = index.row()
        return index

    def onOffloadSelect(self):
        index = self.getIndexFrom(self.offloadTableWidget)
        name = self.offloadNameEntry.text()
        self.runPythonAvionicsCommand("offload --flight_name={0} --flight_num={1}".format(name, index + 1))

    def onPostProcessSelect(self):
        print("Post process index " + str(self.getIndexFrom(self.downloadedFlightsWidget)))

    def onGraphSelect(self):
        print("Graph index " + str(self.getIndexFrom(self.downloadedFlightsWidget)))

    def runPythonAvionicsCommand(self, command):
        """Run this function to call usb cli commands in the module"""
        self.callback_handler.requestCallback(Constants.cli_interface_usb_command_key, command)

    def updateData(self, vehicle_data, updated_data):

        super().updateData(vehicle_data, updated_data)

        # Disable/enable buttons based on if a command is already running
        in_prog = get_value_from_dictionary(vehicle_data, Constants.cli_interface_usb_command_running, False)
        self.setCommandInProgress(in_prog)

        if self.isDictValueUpdated("flights_list"):
            flight_list_str = self.getDictValueUsingSourceKey("flights_list")
            self.recreate_table(flight_list_str)
            self.updateAfterThemeSet()

    def parseOffloadHelp(self, cli_str: str):
        # Filter for lines that start with | and split by return characters
        cli_str = list(filter(lambda line: line.startswith("|"), cli_str.splitlines()))
        # And only return ones with a numeric flight number
        twoDarray = [list(map(lambda s: s.strip(), line.split("|")[1:-1])) for line in cli_str if line.split("|")[1].strip().isnumeric()]

        return twoDarray
