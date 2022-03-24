import os
import time
import math
import sys
import pyqtgraph
from PyQt5.QtCore import QPoint

if sys.platform == "linux":  # I don't even know anymore
    if "QT_QPA_PLATFORM_PLUGIN_PATH" in os.environ:
        os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")  # https://stackoverflow.com/questions/63829991/qt-qpa-plugin-could-not-load-the-qt-platform-plugin-xcb-in-even-though-it

from PyQt5.QtWidgets import QWidget, QGridLayout, QMenu
from pyqtgraph import PlotWidget

from data_helpers import get_qcolor_from_string, first_index_in_list_larger_than

from Widgets.custom_q_widget_base import CustomQWidgetBase

PEN_COLORS = ["red", "blue", "green", "magenta"]


def get_pen_from_line_number(line_number):
    index = line_number % len(PEN_COLORS)
    return pyqtgraph.mkPen(color=PEN_COLORS[index])


def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb


def empty_function(a):
    pass


class GraphWidget(CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None, source_list=None, title=None, time_history=0):
        super().__init__(parent_widget)

        if source_list is None:
            source_list = []

        self.graphWidget = PlotWidget(enableMenu=True)
        self.graphWidget.setLabel('bottom', "Time (s)")
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.addLegend()
        self.graphWidget.getPlotItem().vb.raiseContextMenu = empty_function  # Reach deep into the graph widget and disable its ability to make a context menu
        # Because I need that menu to be displayed the way I want

        self.title = title
        self.update_interval = 0.05
        self.min_x = None
        self.max_x = None

        self.record_new_data = True
        self.max_time_to_keep = time_history
        self.recorded_data_mode = False

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

    def setPlaybackMode(self, use_recorded_data):
        self.recorded_data_mode = use_recorded_data

    def updateData(self, vehicle_data, updated_data):
        if not self.recorded_data_mode:
            if self.record_new_data:
                for source in self.sourceDictionary:
                    value = self.getDictValueUsingSourceKey(source)

                    if source not in self.data_dictionary:
                        self.data_dictionary[source] = [float('nan')]
                        self.time_dictionary[source] = [float('nan')]

                    # <sarcasm> This logic makes perfect sense </sarcasm>
                    # The base goal is to make the last value in the array a nan when the data isn't updated so the graph x axis keeps updating
                    # We need 4 cases because we don't want to overwrite any data, and we don't want NaNs anywhere other than the last spot
                    if self.isDictValueUpdated(source) and math.isnan(self.data_dictionary[source][-1]):
                        self.data_dictionary[source][-1] = value
                        self.time_dictionary[source][-1] = time.time() - self.start_time
                    elif self.isDictValueUpdated(source):
                        self.data_dictionary[source].append(value)
                        self.time_dictionary[source].append(time.time() - self.start_time)
                    elif math.isnan(self.data_dictionary[source][-1]):
                        self.time_dictionary[source][-1] = time.time() - self.start_time
                    else:
                        self.data_dictionary[source].append(float('nan'))
                        self.time_dictionary[source].append(time.time() - self.start_time)

                    oldest_allowable_time = time.time() - self.start_time - self.max_time_to_keep
                    if math.isnan(self.time_dictionary[source][0]):
                        check_index = 1
                    else:
                        check_index = 0

                    if self.max_time_to_keep > 0 and self.time_dictionary[source][check_index] < oldest_allowable_time:
                        slice_index = first_index_in_list_larger_than(self.time_dictionary[source], oldest_allowable_time)
                        self.time_dictionary[source] = [oldest_allowable_time] + self.time_dictionary[source][slice_index:]
                        self.data_dictionary[source] = [float('nan')] + self.data_dictionary[source][slice_index:]
        else:
            for source in self.sourceDictionary:
                [data_series, time_series] = self.getRecordedDictDataUsingSourceKey(source)

                if len(data_series) > 0 and len(data_series) == len(time_series):
                    self.data_dictionary[source] = data_series
                    self.time_dictionary[source] = time_series
                else:
                    self.data_dictionary[source] = [float('nan')]
                    self.time_dictionary[source] = [0]

    def updateInFocus(self):
        """Only re-draw graph if we're looking at it"""
        self.updatePlot()

    def updatePlot(self):
        """Actually updates lines on plot"""

        if time.time() - self.last_update_time < self.update_interval:  # Don't re-draw graphs to quickly
            return
        self.last_update_time = time.time()

        for data_name in self.data_dictionary:
            data_label = self.sourceDictionary[data_name].key_name
            if data_name not in self.plot_line_dictionary:
                self.plot_line_dictionary[data_name] = self.graphWidget.plot(self.time_dictionary[data_name], self.data_dictionary[data_name], name=data_label, pen=get_pen_from_line_number(len(self.plot_line_dictionary)))
            if self.plot_line_dictionary[data_name].name() != data_label:
                self.graphWidget.getPlotItem().removeItem(self.plot_line_dictionary[data_name])
                del self.plot_line_dictionary[data_name]
                self.plot_line_dictionary[data_name] = self.graphWidget.plot(self.time_dictionary[data_name], self.data_dictionary[data_name], name=data_label, pen=get_pen_from_line_number(len(self.plot_line_dictionary)))

            # Connect=finite allows NaN values to be skipped
            if self.min_x is None and self.max_x is None:  # No restrictions
                self.plot_line_dictionary[data_name].setData(self.time_dictionary[data_name], self.data_dictionary[data_name], connect="finite")
            elif self.min_x is None:  # No minimum, truncate maximum
                max_index = first_index_in_list_larger_than(self.time_dictionary[data_name], self.max_x)
                self.plot_line_dictionary[data_name].setData(self.time_dictionary[data_name][0:max_index], self.data_dictionary[data_name][0:max_index], connect="finite")
            elif self.max_x is None:  # No maximum, truncate minimum
                min_index = first_index_in_list_larger_than(self.time_dictionary[data_name], self.min_x)
                self.plot_line_dictionary[data_name].setData(self.time_dictionary[data_name][min_index:], self.data_dictionary[data_name][min_index:], connect="finite")
            else:  # Truncate both max and min
                max_index = first_index_in_list_larger_than(self.time_dictionary[data_name], self.max_x)
                min_index = first_index_in_list_larger_than(self.time_dictionary[data_name], self.min_x)
                self.plot_line_dictionary[data_name].setData(self.time_dictionary[data_name][min_index:max_index], self.data_dictionary[data_name][min_index:max_index], connect="finite")

    def setHistoryLength(self, history_length):
        self.max_time_to_keep = history_length

    def setEnabled(self, enabled):
        self.record_new_data = enabled

    def addCustomMenuItems(self, menu):
        menu.addAction("Clear graph", self.clearGraph)
        menu.addAction("Add Line", self.addLineToPlot)
        remove_line_menu = menu.addMenu("Remove line")
        menu.addSeparator()
        menu.addMenu(self.graphWidget.getPlotItem().vb.menu)
        menu.addMenu(self.graphWidget.getPlotItem().ctrlMenu)

        for key in self.sourceDictionary:
            remove_line_menu.addAction(self.sourceDictionary[key].key_name, lambda name=key: self.removeLineFromPlot(name))

    def addLineToPlot(self):
        num_keys = len(self.sourceDictionary.keys())
        self.addSourceKey("line {}".format(num_keys), float, "", default_value=0)

    def removeLineFromPlot(self, line_name):
        self.removeSourceKey(line_name)
        self.graphWidget.getPlotItem().removeItem(self.plot_line_dictionary[line_name])
        self.plot_line_dictionary[line_name].clear()
        del self.data_dictionary[line_name]
        del self.plot_line_dictionary[line_name]

    def clearGraph(self):
        self.time_dictionary = {}
        self.data_dictionary = {}
        self.start_time = time.time()

    def getNumberOfLines(self):
        return len(self.data_dictionary)

    def setXAxisBounds(self, min_value, max_value):
        self.min_x = min_value
        self.max_x = max_value

    def getLargestTime(self):
        time_val = -1
        for key in self.time_dictionary:
            largest_time = max(self.time_dictionary[key])
            if time_val == -1:
                time_val = largest_time
            else:
                time_val = max(time_val, largest_time)
        return time_val

    def getSmallestTime(self):
        time_val = -1
        for key in self.time_dictionary:
            smallest_time = min(self.time_dictionary[key])
            if time_val == -1:
                time_val = smallest_time
            else:
                time_val = min(time_val, smallest_time)
        return time_val

    def setWidgetColors(self, widget_background_string, text_string, header_text_string, border_string):
        self.graphWidget.setStyleSheet(widget_background_string)

        self.graphWidget.setBackground(get_qcolor_from_string(widget_background_string))
        self.graphWidget.getAxis("left").setTextPen(self.textColor)
        self.graphWidget.getAxis("left").setPen(self.textColor)
        self.graphWidget.getAxis("bottom").setTextPen(self.textColor)
        self.graphWidget.getAxis("bottom").setPen(self.textColor)

        if self.title is not None:
            self.graphWidget.setTitle(self.title, color=get_qcolor_from_string(header_text_string))
