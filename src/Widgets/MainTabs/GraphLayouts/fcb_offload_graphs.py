from src.Widgets.MainTabs.GraphLayouts.graph_layout import GraphLayoutCommon
from PyQt5.QtWidgets import QGridLayout
from src.Widgets.graph_tab_control import GraphTabControl
from src.Widgets.graph_widget import GraphWidget
from src.constants import Constants
from src.data_helpers import interpolate


class FcbOffloadGraphs(GraphLayoutCommon):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        layout = QGridLayout()
        layout.addWidget(self.addWidget(GraphWidget(title="Altitude", source_list=["offload_pos_z", "offload_gps_alt"], )), 1, 1)
        layout.addWidget(self.addWidget(GraphWidget(title="Speeds", source_list=["offload_vel_z", ] )), 1, 2)
        layout.addWidget(self.addWidget(GraphWidget(title="XYZ Accelerations", source_list=[
            "offload_imu1_accel_x_real",
            "offload_imu1_accel_y_real",
            "offload_imu1_accel_z_real",
            "offload_imu2_accel_x_real",
            "offload_imu2_accel_y_real",
            "offload_imu2_accel_z_real", ], )), 1, 3)
        layout.addWidget(self.addWidget(GraphWidget(title="Temperature", source_list=[
            "offload_baro1_temp", "offload_baro2_temp", ], )), 2, 1)

        layout.addWidget(self.addWidget(GraphWidget(title="XYZ Rotational Velocities", source_list=[
            "offload_imu1_gyro_x_real",
            "offload_imu1_gyro_y_real",
            "offload_imu1_gyro_z_real",
            "offload_imu2_gyro_x_real",
            "offload_imu2_gyro_y_real",
            "offload_imu2_gyro_z_real",
        ], )), 2, 2)
        layout.addWidget(self.addWidget(GraphWidget(title="Magnetometer readings", source_list=[
            "offload_imu1_mag_x_real",
            "offload_imu1_mag_y_real",
            "offload_imu1_mag_z_real",
            "offload_imu2_mag_x_real",
            "offload_imu2_mag_y_real",
            "offload_imu2_mag_z_real",
        ], )), 2, 3)
        layout.addWidget(self.addWidget(GraphWidget(title="Pressure", source_list=["offload_baro1_pres", "offload_baro2_pres"], )), 3, 1)
        layout.addWidget(self.addWidget(GraphWidget(title="State", source_list=["offload_state"])), 3, 2)
        layout.addWidget(self.addWidget(GraphWidget(title="Battery", source_list=["offload_battery_voltage"])), 3, 3)
        layout.addWidget(self.graphControlWidget, 4, 1, 1, 3)
        self.setLayout(layout)
