"""
Code to define widget layout to drive warpauv
"""

from PyQt5.QtWidgets import QGridLayout

from Widgets import graph_widget

from constants import Constants

from MainTabs.main_tab_common import TabCommon


class GraphsTab(TabCommon):
    def __init__(self, vehicleName):
        super().__init__(vehicleName)

        layout = QGridLayout()
        layout.addWidget(self.addWidget(graph_widget.GraphWidget(title="Altitude", source_list=[Constants.altitude_key])), 1, 1)
        layout.addWidget(self.addWidget(graph_widget.GraphWidget(title="Vertical Speed", source_list=[Constants.vertical_speed_key])), 1, 2)
        layout.addWidget(self.addWidget(graph_widget.GraphWidget(title="Vertical Acceleration", source_list=[Constants.acceleration_key])), 1, 3)
        layout.addWidget(self.addWidget(graph_widget.GraphWidget(title="RPY Orientation", source_list=[Constants.roll_position_key, Constants.pitch_position_key, Constants.yaw_position_key])), 2, 1)
        layout.addWidget(self.addWidget(graph_widget.GraphWidget(title="XYZ Rotational Velocities", source_list=[Constants.rotational_velocity_x_key, Constants.rotational_velocity_y_key, Constants.rotational_velocity_z_key])), 2, 2)
        layout.addWidget(self.addWidget(graph_widget.GraphWidget(title="XYZ Accelerations", source_list=[Constants.acceleration_x_key, Constants.acceleration_y_key, Constants.acceleration_z_key])), 2, 3)
        layout.addWidget(self.addWidget(graph_widget.GraphWidget(title="Ground Speed", source_list=[Constants.ground_speed_key])), 3, 1)
        layout.addWidget(self.addWidget(graph_widget.GraphWidget()), 3, 2)
        layout.addWidget(self.addWidget(graph_widget.GraphWidget()), 3, 3)

        self.setLayout(layout)
