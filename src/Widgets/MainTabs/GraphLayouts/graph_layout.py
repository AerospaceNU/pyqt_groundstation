

from src.Widgets.MainTabs.main_tab_common import TabCommon
from src.Widgets.custom_q_widget_base import CustomQWidgetBase
from PyQt5.QtWidgets import QGridLayout
from src.Widgets.graph_tab_control import GraphTabControl
from src.Widgets.graph_widget import GraphWidget
from src.constants import Constants
from src.data_helpers import interpolate


class GraphLayoutCommon(TabCommon):
    def __init__(self,  parent=None):
        super().__init__( parent=parent)

        self.graphControlWidget = self.addWidget(GraphTabControl())

        self.slider_min = 0
        self.slider_max = 1000

        self.graphControlWidget.rangeSlider.valueChanged.connect(self.onSliderValueChange)
        self.graphControlWidget.resetGraphButton.pressed.connect(self.clearAllGraphs)

    def clearAllGraphs(self):
        for widget in self.widgetList:
            if type(widget) == GraphWidget:
                widget.clearGraph()

    def onSliderValueChange(self, data):
        self.slider_min = data[0]
        self.slider_max = data[1]

    def customUpdateVehicleData(self, data):
        graphs_enabled = self.graphControlWidget.graphsEnabled()
        try:
            graphs_history = float(self.graphControlWidget.getHistoryBoxValue())
        except (TypeError, ValueError):
            graphs_history = 0

        recorded_data_enabled = self.graphControlWidget.playbackEnabled()

        largest_time_list = []
        smallest_time_list = []

        for widget in self.widgetList:
            if type(widget) == GraphWidget and widget.getNumberOfLines() > 0:
                largest_time_list.append(widget.getLargestTime())
                smallest_time_list.append(widget.getSmallestTime())

        if smallest_time_list == []:
            smallest_time_list.append(0)
        if largest_time_list == []:
            largest_time_list.append(1)
        smallest_time = min(smallest_time_list)
        largest_time = max(max(largest_time_list), smallest_time + 1)

        if self.slider_min == 0:
            graph_min = None
        else:
            graph_min = interpolate(self.slider_min, 0, 1000, smallest_time, largest_time)

        if self.slider_max == 1000:
            graph_max = None
        else:
            graph_max = interpolate(self.slider_max, 0, 1000, smallest_time, largest_time)

        for widget in self.widgetList:
            if type(widget) == GraphWidget:
                widget.setXAxisBounds(graph_min, graph_max)
                widget.setEnabled(graphs_enabled)
                widget.setHistoryLength(graphs_history)
                widget.setPlaybackMode(recorded_data_enabled)
