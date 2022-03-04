import os
import time
import sys
import pyqtgraph

if sys.platform == "linux":  # I don't even know anymore
    os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")  # https://stackoverflow.com/questions/63829991/qt-qpa-plugin-could-not-load-the-qt-platform-plugin-xcb-in-even-though-it

from PyQt5.QtWidgets import QWidget, QGridLayout
from pyqtgraph import PlotWidget

from data_helpers import get_qcolor_from_string

from Widgets.custom_q_widget_base import CustomQWidgetBase

PEN_COLORS = ["red", "blue", "green", "magenta"]


def get_pen_from_line_number(line_number):
    index = line_number % len(PEN_COLORS)
    return pyqtgraph.mkPen(color=PEN_COLORS[index])


def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb


class GraphWidget(CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None, source_list=None, title=None):
        super().__init__(parent_widget)

        if source_list is None:
            source_list = []

        self.graphWidget = PlotWidget()
        self.graphWidget.setLabel('bottom', "Time (s)")
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.addLegend()
        self.title = title
        self.update_interval = 0.01

        if title is not None:
            self.graphWidget.setTitle(title)

        for i in range(len(source_list)):
            source = source_list[i]
            self.addSourceKey("line {}".format(i), float, source, default_value=0)

        self.data_dictionary = {}  # Stores the history for each data field we
        self.time_dictionary = {}  # Stores the times we've taken data at (the x axis) for each field we track
        self.plot_line_dictionary = {}  # Stores the plot line objects
        self.start_time = time.time()
        self.last_update_time = time.time()

        self.updatePlot()

        layout = QGridLayout()
        layout.addWidget(self.graphWidget)
        self.setLayout(layout)

        if parent_widget is not None:
            self.setGeometry(100, 100, 680, 500)
        else:
            layout.setContentsMargins(1, 1, 1, 1)

        self.show()

    def updateData(self, vehicle_data):
        if time.time() - self.last_update_time < self.update_interval:
            return
        self.last_update_time = time.time()

        for source in self.sourceList:
            value = self.getDictValueUsingSourceKey(source)

            if source not in self.data_dictionary:
                self.data_dictionary[source] = []
                self.time_dictionary[source] = []
            self.data_dictionary[source].append(value)
            self.time_dictionary[source].append(time.time() - self.start_time)

        self.updatePlot()

    def updatePlot(self):
        """Actually updates lines on plot"""
        for data_name in self.data_dictionary:
            data_label = self.sourceList[data_name].key_name
            if data_name not in self.plot_line_dictionary:
                self.plot_line_dictionary[data_name] = self.graphWidget.plot(self.time_dictionary[data_name], self.data_dictionary[data_name], name=data_label, pen=get_pen_from_line_number(len(self.plot_line_dictionary)))
            if self.plot_line_dictionary[data_name].name() != data_label:
                self.graphWidget.getPlotItem().removeItem(self.plot_line_dictionary[data_name])
                del self.plot_line_dictionary[data_name]
                self.plot_line_dictionary[data_name] = self.graphWidget.plot(self.time_dictionary[data_name], self.data_dictionary[data_name], name=data_label, pen=get_pen_from_line_number(len(self.plot_line_dictionary)))

            self.plot_line_dictionary[data_name].setData(self.time_dictionary[data_name], self.data_dictionary[data_name])

    def addCustomMenuItems(self, menu):
        menu.addAction("Clear graph", self.clearGraph)
        menu.addAction("Add Line", self.addLineToPlot)

    def addLineToPlot(self):
        num_keys = len(self.sourceList.keys())
        self.addSourceKey("line {}".format(num_keys), float, "", default_value=0)

    def clearGraph(self):
        self.time_dictionary = {}
        self.data_dictionary = {}
        self.start_time = time.time()

    def setWidgetColors(self, widget_background_string, text_string, header_text_string, border_string):
        self.graphWidget.setStyleSheet(widget_background_string)

        self.graphWidget.setBackground(get_qcolor_from_string(widget_background_string))
        self.graphWidget.getAxis("left").setTextPen(self.textColor)
        self.graphWidget.getAxis("left").setPen(self.textColor)
        self.graphWidget.getAxis("bottom").setTextPen(self.textColor)
        self.graphWidget.getAxis("bottom").setPen(self.textColor)

        if self.title is not None:
            self.graphWidget.setTitle(self.title, color=get_qcolor_from_string(header_text_string))
