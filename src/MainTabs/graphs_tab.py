"""
A bunch of graphs
"""

from PyQt5.QtWidgets import QGridLayout

from src.constants import Constants
from src.data_helpers import interpolate
from src.MainTabs.main_tab_common import TabCommon
from src.Widgets.graph_tab_control import GraphTabControl
from src.Widgets.graph_widget import GraphWidget


class GraphsTab(TabCommon):
    def __init__(self, tab_name, parent=None):
        super().__init__(tab_name, parent=parent)

        self.graphControlWidget = self.addWidget(GraphTabControl())

        self.slider_min = 0
        self.slider_max = 1000

        layout = QGridLayout()
        layout.addWidget(
            self.addWidget(
                GraphWidget(
                    title="Altitude",
                    source_list=[Constants.altitude_key, Constants.gps_alt_key],
                )
            ),
            1,
            1,
        )
        layout.addWidget(
            self.addWidget(
                GraphWidget(
                    title="Speeds",
                    source_list=[
                        Constants.vertical_speed_key,
                        Constants.ground_speed_key,
                    ],
                )
            ),
            1,
            2,
        )
        layout.addWidget(
            self.addWidget(
                GraphWidget(
                    title="XYZ Accelerations",
                    source_list=[
                        Constants.acceleration_x_key,
                        Constants.acceleration_y_key,
                        Constants.acceleration_z_key,
                    ],
                )
            ),
            1,
            3,
        )
        layout.addWidget(
            self.addWidget(
                GraphWidget(
                    title="RPY Orientation",
                    source_list=[
                        Constants.roll_position_key,
                        Constants.pitch_position_key,
                        Constants.yaw_position_key,
                    ],
                )
            ),
            2,
            1,
        )
        layout.addWidget(
            self.addWidget(
                GraphWidget(
                    title="XYZ Rotational Velocities",
                    source_list=[
                        Constants.rotational_velocity_x_key,
                        Constants.rotational_velocity_y_key,
                        Constants.rotational_velocity_z_key,
                    ],
                )
            ),
            2,
            2,
        )
        layout.addWidget(
            self.addWidget(
                GraphWidget(
                    title="Magnetometer readings",
                    source_list=[
                        Constants.magnetometer_x_key,
                        Constants.magnetometer_y_key,
                        Constants.magnetometer_z_key,
                    ],
                )
            ),
            2,
            3,
        )
        layout.addWidget(
            self.addWidget(
                GraphWidget(
                    title="Pressure, Pressure, & Pressure",
                    source_list=[
                        Constants.barometer_pressure_key,
                        Constants.barometer_pressure_2_key,
                        Constants.press_ref_key,
                    ],
                )
            ),
            3,
            1,
        )
        layout.addWidget(
            self.addWidget(
                GraphWidget(title="State", source_list=[Constants.fcb_state_number_key])
            ),
            3,
            2,
        )
        layout.addWidget(
            self.addWidget(
                GraphWidget(title="RSSI", source_list=[Constants.rssi_val_key])
            ),
            3,
            3,
        )
        layout.addWidget(self.graphControlWidget, 4, 1, 1, 3)
        self.setLayout(layout)

        self.graphControlWidget.rangeSlider.valueChanged.connect(
            self.onSliderValueChange
        )
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

        smallest_time = min(smallest_time_list)
        largest_time = max(max(largest_time_list), smallest_time + 1)

        if self.slider_min == 0:
            graph_min = None
        else:
            graph_min = interpolate(
                self.slider_min, 0, 1000, smallest_time, largest_time
            )

        if self.slider_max == 1000:
            graph_max = None
        else:
            graph_max = interpolate(
                self.slider_max, 0, 1000, smallest_time, largest_time
            )

        for widget in self.widgetList:
            if type(widget) == GraphWidget:
                widget.setXAxisBounds(graph_min, graph_max)
                widget.setEnabled(graphs_enabled)
                widget.setHistoryLength(graphs_history)
                widget.setPlaybackMode(recorded_data_enabled)
