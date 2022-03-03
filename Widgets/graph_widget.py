import os
import time
import sys

if sys.platform == "linux":  # I don't even know anymore
    os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")  # https://stackoverflow.com/questions/63829991/qt-qpa-plugin-could-not-load-the-qt-platform-plugin-xcb-in-even-though-it

from PyQt5.QtWidgets import QWidget, QGridLayout
from pyqtgraph import PlotWidget

from constants import Constants
from Widgets.custom_q_widget_base import CustomQWidgetBase


class GraphWidget(CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None, source_list=None, title=None):
        super().__init__(parent_widget)

        if source_list is None:
            source_list = []

        self.graphWidget = PlotWidget()
        self.graphWidget.setLabel('bottom', "Time (s)")
        self.graphWidget.showGrid(x=True, y=True)

        if title is not None:
            self.graphWidget.setTitle(title)

        for i in range(len(source_list)):
            source = source_list[i]
            self.addSourceKey("line_{}".format(i), float, source, default_value=0)

        self.data_dictionary = {}
        self.plot_line_dictionary = {}
        self.time_list = []
        self.start_time = time.time()

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
        self.time_list.append(time.time() - self.start_time)

        for source in self.sourceList:
            value = self.getDictValueUsingSourceKey(source)

            if source not in self.data_dictionary:
                self.data_dictionary[source] = []
            self.data_dictionary[source].append(value)

        self.updatePlot()

    def updatePlot(self):
        for data_name in self.data_dictionary:
            if data_name not in self.plot_line_dictionary:
                self.plot_line_dictionary[data_name] = self.graphWidget.plot(self.time_list, self.data_dictionary[data_name])

            self.plot_line_dictionary[data_name].setData(self.time_list, self.data_dictionary[data_name])

    def addCustomMenuItems(self, menu):
        menu.addAction("Clear graph", self.clearGraph)
        menu.addAction("Add Line", self.addLineToPlot)

    def addLineToPlot(self):
        num_keys = len(self.sourceList.keys())
        self.addSourceKey("line_{}".format(num_keys), float, "", default_value=0)

        self.time_list = []  # Hack to clear stored data without clearing the graph
        self.data_dictionary = {}  # We need to clear stored data to keep all the lists the same length

    def clearGraph(self):
        self.time_list = []
        self.data_dictionary = {}
        self.start_time = time.time()
        # self.plot_line_dictionary = {}

    def setWidgetColors(self, widget_background_string, text_string, header_text_string, border_string):
        self.graphWidget.setStyleSheet(widget_background_string)
