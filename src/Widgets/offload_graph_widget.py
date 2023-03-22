"""
Offload Graph
"""

import os
import shutil
from os import listdir
from os.path import isfile, join

import pandas as pd
import pyqtgraph
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)
from pyqtgraph import PlotWidget
from qtrangeslider import QRangeSlider

from src.constants import Constants
from src.data_helpers import first_index_in_list_larger_than, interpolate
from src.Modules.DataInterfaceTools.pyqtgraph_helper import get_pen_from_line_number
from src.python_avionics.model.fcb_offload_analyzer import FcbOffloadAnalyzer
from src.Widgets import custom_q_widget_base


def rgb_to_hex(rgb):
    return "%02x%02x%02x" % rgb


class OffloadGraphWidget(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        self.vbox = layout

        self.widgetList = []

        # self.source = Constants.cli_interface_key
        self.titleBox = QLabel()
        self.title = "Offload and Graph"
        self.titleBox.setText(self.title)
        self.titleBox.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        layout.addWidget(self.titleBox)

        # --- OFFLOAD ---
        temp = QHBoxLayout()
        self.add(QPushButton(text="Import File"), layout=temp, onClick=self.onFileImport)
        self.add(QPushButton(text="Refresh Data"), layout=temp, onClick=self.refreshTable)
        layout.addLayout(temp)

        self.downloadedTableWidget = QTableWidget()
        self.downloadedTableWidget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.downloadedTableWidget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.downloadedTableWidget.doubleClicked.connect(self.onFlightSelected)
        self.downloadedTableWidget.setMinimumHeight(300)
        self.downloadedTableWidget.setColumnCount(3)
        self.downloadedTableWidget.setColumnWidth(0, 160)
        self.downloadedTableWidget.setColumnWidth(1, 150)
        self.downloadedTableWidget.setColumnWidth(2, 200)
        self.downloadedTableWidget.setHorizontalHeaderLabels(["Name", "Raw", "Post-processed"])
        self.downloadedTableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.downloadedTableWidget.itemSelectionChanged.connect(self.updateButtons)
        layout.addWidget(self.downloadedTableWidget)

        self.recreate_table(self.getFlights())

        temp = QHBoxLayout()
        self.postButton = self.add(QPushButton(text="Select Flight for Post"), layout=temp, onClick=self.onFlightSelected)
        self.simButton = self.add(QPushButton(text="Simulate selected"), layout=temp, onClick=self.onSimulateSelected)
        self.graphButton = self.add(QPushButton(text="Graph selected"), layout=temp, onClick=self.onGraphSelected)
        self.simButton.setEnabled(False)
        self.graphButton.setEnabled(False)
        layout.addLayout(temp)

        self.addSourceKey("flights_list", str, Constants.cli_flights_list_key, default_value="", hide_in_drop_down=True)

        self.altitudeGraph = PlotWidget()
        self.altitudeGraph.setMaximumHeight(400)
        self.altitudeGraph.setLabel("bottom", "Time (s)")
        self.altitudeGraph.showGrid(x=True, y=True)
        self.altitudeGraph.addLegend()
        self.altitudeLine = None
        layout.addWidget(self.altitudeGraph)

        self.rangeSlider = QRangeSlider(Qt.Horizontal)
        self.rangeSlider.setRange(0, 1000)
        self.rangeSlider.setSliderPosition([0, 1000])
        self.widgetList.append(self.rangeSlider)
        layout.addWidget(self.rangeSlider)

        self.rangeSlider.valueChanged.connect(self.onSliderChange)

        self.add(QPushButton(text="Actually Post-Process"), onClick=self.onPostProcessSelect)

        self.minXLine = None
        self.maxXLine = None

        self.min_x = 0
        self.max_x = 0
        self.altitude_time_arr = []
        self.altitude_data_arr = []

        self.slider_min = 0
        self.slider_max = 0

        self.raw_file_path = ""
        self.raw_file = None

        self.setLayout(layout)

    def onSliderChange(self, data):
        self.slider_min = data[0]
        self.slider_max = data[1]

        if len(self.altitude_time_arr) == 0:  # We don't have data yet
            return

        smallest_time = min(self.altitude_time_arr)
        largest_time = max(self.altitude_time_arr)

        if self.slider_min == 0:
            graph_min = None
        else:
            graph_min = interpolate(self.slider_min, 0, 1000, smallest_time, largest_time)

        if self.slider_max == 1000:
            graph_max = None
        else:
            graph_max = interpolate(self.slider_max, 0, 1000, smallest_time, largest_time)

        self.min_x = graph_min
        self.max_x = graph_max

        # self.altitudeGraph.setXAxisBounds(graph_min, graph_max)

        # Connect=finite allows NaN values to be skipped
        if self.min_x is None and self.max_x is None:  # No restrictions
            self.altitudeLine.setData(self.altitude_time_arr, self.altitude_data_arr, connect="finite")
            self.min_x = smallest_time
            self.max_x = largest_time
        elif self.min_x is None:  # No minimum, truncate maximum
            max_index = first_index_in_list_larger_than(self.altitude_time_arr, self.max_x)
            self.altitudeLine.setData(self.altitude_time_arr[0:max_index], self.altitude_data_arr[0:max_index], connect="finite")
            self.min_x = smallest_time
        elif self.max_x is None:  # No maximum, truncate minimum
            min_index = first_index_in_list_larger_than(self.altitude_time_arr, self.min_x)
            self.altitudeLine.setData(self.altitude_time_arr[min_index:], self.altitude_data_arr[min_index:], connect="finite")
            self.max_x = largest_time
        else:  # Truncate both max and min
            max_index = first_index_in_list_larger_than(self.altitude_time_arr, self.max_x)
            min_index = first_index_in_list_larger_than(self.altitude_time_arr, self.min_x)
            self.altitudeLine.setData(self.altitude_time_arr[min_index:max_index], self.altitude_data_arr[min_index:max_index], connect="finite")

        self.altitudeGraph.setXRange(self.min_x, self.max_x)

        if self.min_x > self.minXLine.getXPos():
            self.minXLine.setPos(self.min_x)
        if self.max_x < self.maxXLine.getXPos():
            self.maxXLine.setPos(self.max_x)

    def recreate_table(self, flight_array):
        if len(flight_array) > 0:
            self.downloadedTableWidget.setRowCount(len(flight_array))
        else:
            self.downloadedTableWidget.setRowCount(0)
        for i in range(len(flight_array)):
            row = flight_array[i]
            self.downloadedTableWidget.setItem(i, 0, QTableWidgetItem(row[0]))
            self.downloadedTableWidget.setItem(i, 1, QTableWidgetItem(row[1]))
            self.downloadedTableWidget.setItem(i, 2, QTableWidgetItem(row[2]))

            for j in range(3):
                item = self.downloadedTableWidget.item(i, j)
                if item is not None:
                    item.setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

    @staticmethod
    def getFlights():
        my_path = "output"
        if not os.path.exists(my_path):
            return []
        flight_files = [f for f in listdir(my_path) if isfile(join(my_path, f)) and (f.endswith("-output-FCB.csv") or f.endswith("-output-FCB-post.csv"))]

        ret = []
        for file in set(map(lambda it: it.replace("-output-FCB.csv", "").replace("-output-FCB-post.csv", ""), flight_files)):
            has_raw = "Yes" if file + "-output-FCB.csv" in flight_files else "No"
            has_post = "Yes" if file + "-output-FCB-post.csv" in flight_files else "No"
            ret.append([file.replace("-output-FCB.csv", ""), has_raw, has_post])

        return ret

    def refreshTable(self):
        self.recreate_table(self.getFlights())
        self.updateAfterThemeSet()
        self.updateButtons()

    def add(self, widget, layout=None, onClick=None):
        if layout is None:
            layout = self.vbox
        self.widgetList.append(widget)
        layout.addWidget(widget)

        if onClick:
            widget.clicked.connect(onClick)

        return widget

    def onFileImport(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "All Files (*);;CSV Files (*.csv)", options=options)
        if fileName:
            # print(fileName)

            if not os.path.exists("output"):
                os.mkdir("output")
            shutil.copy2(fileName, "output/")

            self.refreshTable()

    @staticmethod
    def getFlightFrom(listWidget):
        indexes = listWidget.selectedItems()
        if len(indexes) < 1:
            return

        index = indexes[0]
        return index.text()

    def onFlightSelected(self):
        flightName = self.getFlightFrom(self.downloadedTableWidget)

        self.raw_file_path = os.path.join("output", f"{flightName}-output-FCB.csv")
        if not os.path.exists(self.raw_file_path):
            return
        csv = pd.read_csv(self.raw_file_path)
        self.raw_file = csv

        # Hack since timestamp_s is in ms
        csv["timestamp_s"] = csv["timestamp_s"] / 1000

        self.altitude_time_arr = list(csv["timestamp_s"])
        self.altitude_data_arr = list(csv["pos_z"])
        if self.altitudeLine is not None:
            self.altitudeGraph.getPlotItem().removeItem(self.altitudeLine)
        self.altitudeLine = self.altitudeGraph.plot(self.altitude_time_arr, self.altitude_data_arr, name="Altitude (m)", pen=get_pen_from_line_number(0))

        self.min_x = min(self.altitude_time_arr)
        self.max_x = max(self.altitude_time_arr)

        self.altitudeGraph.setXRange(self.min_x, self.max_x)

        if self.minXLine is None:
            self.minXLine = pyqtgraph.InfiniteLine(movable=True, name="Flight start")
            self.maxXLine = pyqtgraph.InfiniteLine(movable=True, name="Flight end")
            self.altitudeGraph.addItem(self.minXLine)
            self.altitudeGraph.addItem(self.maxXLine)
        self.minXLine.setPos(self.min_x)
        self.maxXLine.setPos(self.max_x)

    def onPostProcessSelect(self):
        if self.minXLine is None:  # We don't have data yet
            return

        FcbOffloadAnalyzer.analyze_time_range(self.raw_file, self.minXLine.getXPos(), self.maxXLine.getXPos(), self.raw_file_path)
        self.refreshTable()

    def onGraphSelected(self):
        pass

    def onSimulateSelected(self):
        pass

    def updateButtons(self):
        flights = self.getFlights()
        flightName = self.getFlightFrom(self.downloadedTableWidget)

        for flight in flights:
            if flight[0] == flightName:
                has_post = flight[2] == "Yes"
                self.simButton.setEnabled(has_post)
                self.graphButton.setEnabled(has_post)
                self.postButton.setEnabled(flight[1] == "Yes")

    def customUpdateAfterThemeSet(self):
        self.altitudeGraph.setBackground(self.palette().color(self.backgroundRole()))
