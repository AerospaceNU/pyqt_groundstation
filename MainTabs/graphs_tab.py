"""
Code to define widget layout to drive warpauv
"""

from PyQt5.QtWidgets import QGridLayout

from Widgets.graph_widget import GraphWidget
from Widgets.graph_tab_control import GraphTabControl

from constants import Constants
from data_helpers import interpolate

from MainTabs.main_tab_common import TabCommon


class GraphsTab(TabCommon):
    def __init__(self, vehicleName):
        super().__init__(vehicleName)

        self.graphControlWidget = GraphTabControl()
        self.addWidget(self.graphControlWidget)

        self.slider_min = 0
        self.slider_max = 1000

        layout = QGridLayout()
        layout.addWidget(self.addWidget(GraphWidget(title="Altitude", source_list=[Constants.altitude_key])), 1, 1)
        layout.addWidget(self.addWidget(GraphWidget(title="Vertical Speed", source_list=[Constants.vertical_speed_key])), 1, 2)
        layout.addWidget(self.addWidget(GraphWidget(title="Vertical Acceleration", source_list=[Constants.acceleration_key])), 1, 3)
        layout.addWidget(self.addWidget(GraphWidget(title="RPY Orientation", source_list=[Constants.roll_position_key, Constants.pitch_position_key, Constants.yaw_position_key])), 2, 1)
        layout.addWidget(self.addWidget(GraphWidget(title="XYZ Rotational Velocities", source_list=[Constants.rotational_velocity_x_key, Constants.rotational_velocity_y_key, Constants.rotational_velocity_z_key])), 2, 2)
        layout.addWidget(self.addWidget(GraphWidget(title="XYZ Accelerations", source_list=[Constants.acceleration_x_key, Constants.acceleration_y_key, Constants.acceleration_z_key])), 2, 3)
        layout.addWidget(self.addWidget(GraphWidget(title="Ground Speed", source_list=[Constants.ground_speed_key])), 3, 1)
        layout.addWidget(self.addWidget(GraphWidget()), 3, 2)
        layout.addWidget(self.addWidget(GraphWidget()), 3, 3)
        layout.addWidget(self.graphControlWidget, 4, 1, 1, 3)
        self.setLayout(layout)

        self.graphControlWidget.rangeSlider.valueChanged.connect(self.onSliderValueChange)
        self.graphControlWidget.resetGraphButton.pressed.connect(self.clearAllGraphs)

    def clearAllGraphs(self):
        for widget in self.widgetList:
            if type(widget) == GraphWidget:
                widget.clearGraph()

    def onSliderValueChange(self, data):
        self.slider_min = data[0]
        self.slider_max = data[1]

    def customUpdate(self, data):
        graphs_enabled = self.graphControlWidget.graphsEnabled()

        largest_time_list = []
        smallest_time_list = []

        for widget in self.widgetList:
            if type(widget) == GraphWidget and widget.getNumberOfLines() > 0:
                largest_time_list.append(widget.getLargestTime())
                smallest_time_list.append(widget.getSmallestTime())

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
