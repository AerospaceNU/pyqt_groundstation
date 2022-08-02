from PyQt5.QtWidgets import QGridLayout

from src.constants import Constants
from src.Widgets.graph_widget import GraphWidget
from src.Widgets.MainTabs.GraphLayouts.graph_layout import GraphLayoutCommon


class FcbTelemetryGraphs(GraphLayoutCommon):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

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
        layout.addWidget(self.addWidget(GraphWidget(title="State", source_list=[Constants.fcb_state_number_key])), 3, 2)
        layout.addWidget(self.addWidget(GraphWidget(title="RSSI", source_list=[Constants.rssi_val_key])), 3, 3)
        layout.addWidget(self.graphControlWidget, 4, 1, 1, 3)
        self.setLayout(layout)
