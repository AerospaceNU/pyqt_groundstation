"""
Prop Sequencer Widget
Shows the current sequence and abort status
"""

from datetime import datetime

import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.constants import Constants
from src.CustomLogging.dpf_logger import MAIN_GUI_LOGGER, set_test_name
from src.Widgets import custom_q_widget_base


class LoggerControlWidget(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)

        title_widget = QLabel()
        title_widget.setText("Logger Control")
        title_widget.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_widget)

        name_hbox = QHBoxLayout()
        layout.addLayout(name_hbox)
        name_hbox.addWidget(QLabel(text="Test Name"))
        self.textedit = QLineEdit()
        self.textedit.setText(self.widgetSettings.get("testname", "UNKNOWN"))
        name_hbox.addWidget(self.textedit)

        confirm = QPushButton(text="Set Test")
        confirm.clicked.connect(self.onClick)
        name_hbox.addWidget(confirm)

        confirm = QPushButton(text="End Test")
        confirm.clicked.connect(self.onEnd)
        name_hbox.addWidget(confirm)

        # Now add a table that shows test name, start time, duration
        self.offloadTableWidget = QTableWidget()
        self.offloadTableWidget.setColumnCount(3)
        self.offloadTableWidget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.offloadTableWidget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.offloadTableWidget.setHorizontalHeaderLabels(["Date", "Name", "Duration"])
        self.offloadTableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.offloadTableWidget.setColumnWidth(0, 160)
        self.offloadTableWidget.setColumnWidth(1, 150)
        self.offloadTableWidget.setColumnWidth(2, 130)
        layout.addWidget(self.offloadTableWidget)

        self.named_button = QCheckBox(text="Only show named?")
        self.named_button.clicked.connect(self.recreate_table)
        self.named_button.setChecked(True if self.widgetSettings.get("only_named", False) == "True" else False)
        layout.addWidget(self.named_button)

        self.recreate_table()

        # Now buttons to set recorded data for a given log file
        button_hbox = QHBoxLayout()
        fcb_button = QPushButton("Set FCB log data")
        prop_button = QPushButton("Set Prop log data")
        prop_button.clicked.connect(self.set_prop_data)
        button_hbox.addWidget(fcb_button)
        button_hbox.addWidget(prop_button)
        layout.addLayout(button_hbox)

    def getIndexFrom(self, listWidget):
        indexes = listWidget.selectedIndexes()
        if len(indexes) < 1:
            return

        index = indexes[0]
        index = index.row()
        return index

    def set_prop_data(self):
        # We know the currently selected row, so index into our dict
        current_idx = self.getIndexFrom(self.offloadTableWidget)
        flight_name = self.log_paths[current_idx]
        # Use a callback to tell main GUI that we want to set recorded data
        self.requestCallback(Constants.set_recorded_data_callback_id, [Constants.InterfaceNames.prop_websocket, flight_name])

    def recreate_table(self):
        # Save checked state
        self.widgetSettings.save("only_named", str(self.named_button.isChecked()))

        log_files = MAIN_GUI_LOGGER.get_all_runs()
        self.log_files = log_files
        # dict with rows in format
        #    name: (date, duration, has_groundstation, has_prop)

        row_count = max(len(log_files), 1)
        self.offloadTableWidget.setRowCount(row_count)

        self.log_paths = []

        # We're filtering so need to keep track of row number manually
        row_number = 0
        for row in log_files:
            row_data = log_files[row]
            if row.count("_") > 1:
                name = row[row.find("_", row.find("_") + 1) + 1 :]  # everything after second underscore
            else:
                name = ""

            if self.named_button.isChecked() and name == "":
                row_count = row_count - 1
                continue

            self.offloadTableWidget.setItem(row_number, 0, QTableWidgetItem(str(datetime.fromtimestamp(row_data[0]))))
            self.offloadTableWidget.setItem(row_number, 1, QTableWidgetItem(name))
            self.offloadTableWidget.setItem(row_number, 2, QTableWidgetItem(str(row_data[1])))

            for j in range(3):
                item = self.offloadTableWidget.item(row_number, j)
                if item is not None:
                    item.setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

            row_number = row_number + 1
            self.log_paths.append(row)

        self.offloadTableWidget.setRowCount(row_count)

    def onClick(self):
        testName = self.textedit.text()
        self.widgetSettings.save("testname", testName)
        set_test_name(testName)

    def onEnd(self):
        set_test_name("")
