"""Post-processes and analyzes data from FCB offload."""
import os.path
from argparse import ArgumentParser
from typing import Callable, Tuple

import matplotlib.cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backend_bases import MouseButton

from src.python_avionics.model.fcb_cli import FcbCli
from src.python_avionics.model.serial_port import SerialPortManager
from src.python_avionics.view.console_view import ConsoleView


class FcbOffloadAnalyzer:
    """Post-processes and analyzes data from FCB offload, using given filepath."""

    def __init__(
        self,
        offload_data_filepath: str,
        select_time_limits_cb: Callable[[pd.DataFrame, str, str], Tuple[float, float]],
    ) -> None:
        """
        Initialize FCB offloader by storing filepath.

        :param offload_data_filepath: Path to offloaded data (csv)
        :param select_time_limits_cb: Callback to get time boundaries from dataframe series of (timestamp, altitude)
        """
        self._offload_data_filepath = offload_data_filepath
        self._select_time_limits_cb = select_time_limits_cb

    def analyze(self) -> str:
        """
        Read output CSV into dataframe, get time range from user, and process into new CSV

        :return CSV output filepath
        """
        df = pd.read_csv(self._offload_data_filepath)

        # Ask for data to keep of launch and trim
        start_time, end_time = self._select_time_limits_cb(df, "timestamp_s", "pos_z")

        df = df[(df["timestamp_s"] > start_time) & (df["timestamp_s"] < end_time)]

        # Turn GPS into degrees and minutes from float
        df["gps_lat_mod"] = (np.floor(np.abs(df["gps_lat"]) / 100) + (np.abs(df["gps_lat"]) % 100 / 60)) * np.sign(df["gps_lat"])
        df["gps_long_mod"] = (np.floor(np.abs(df["gps_long"]) / 100) + (np.abs(df["gps_long"]) % 100 / 60)) * np.sign(df["gps_long"])

        # Start processing on trimmed data. Multipliers come from resolutions converted to MKS units
        k_accel_mult = 0.0071784678
        k_gyro_mult = 0.000305432618
        k_mag_mult = 0.00058
        k_high_g_accel_multiplier = 0.02942
        df["imu1_accel_x_real"] = df["imu1_accel_x"] * k_accel_mult
        df["imu1_accel_y_real"] = df["imu1_accel_y"] * k_accel_mult
        df["imu1_accel_z_real"] = df["imu1_accel_z"] * k_accel_mult
        df["imu2_accel_x_real"] = df["imu2_accel_x"] * k_accel_mult
        df["imu2_accel_y_real"] = df["imu2_accel_y"] * k_accel_mult
        df["imu2_accel_z_real"] = df["imu2_accel_z"] * k_accel_mult
        df["imu1_gyro_x_real"] = df["imu1_gyro_x"] * k_gyro_mult
        df["imu1_gyro_y_real"] = df["imu1_gyro_y"] * k_gyro_mult
        df["imu1_gyro_z_real"] = df["imu1_gyro_z"] * k_gyro_mult
        df["imu2_gyro_x_real"] = df["imu2_gyro_x"] * k_gyro_mult
        df["imu2_gyro_y_real"] = df["imu2_gyro_y"] * k_gyro_mult
        df["imu2_gyro_z_real"] = df["imu2_gyro_z"] * k_gyro_mult
        df["imu1_mag_x_real"] = df["imu1_mag_x"] * k_mag_mult
        df["imu1_mag_y_real"] = df["imu1_mag_y"] * k_mag_mult
        df["imu1_mag_z_real"] = df["imu1_mag_z"] * k_mag_mult
        df["imu2_mag_x_real"] = df["imu2_mag_x"] * k_mag_mult
        df["imu2_mag_y_real"] = df["imu2_mag_y"] * k_mag_mult
        df["imu2_mag_z_real"] = df["imu2_mag_z"] * k_mag_mult
        df["imu_accel_x_avg"] = df[["imu1_accel_x_real", "imu2_accel_x_real"]].mean(axis=1)
        df["imu_accel_y_avg"] = df[["imu1_accel_y_real", "imu2_accel_y_real"]].mean(axis=1)
        df["imu_accel_z_avg"] = df[["imu1_accel_z_real", "imu2_accel_z_real"]].mean(axis=1)
        df["imu_gyro_x_avg"] = df[["imu1_gyro_x_real", "imu2_gyro_x_real"]].mean(axis=1)
        df["imu_gyro_y_avg"] = df[["imu1_gyro_y_real", "imu2_gyro_y_real"]].mean(axis=1)
        df["imu_gyro_z_avg"] = df[["imu1_gyro_z_real", "imu2_gyro_z_real"]].mean(axis=1)
        df["imu_mag_x_avg"] = df[["imu1_mag_x_real", "imu2_mag_x_real"]].mean(axis=1)
        df["imu_mag_y_avg"] = df[["imu1_mag_y_real", "imu2_mag_y_real"]].mean(axis=1)
        df["imu_mag_z_avg"] = df[["imu1_mag_z_real", "imu2_mag_z_real"]].mean(axis=1)
        df["high_g_accel_x_real"] = df["high_g_accel_x"] * k_high_g_accel_multiplier
        df["high_g_accel_y_real"] = df["high_g_accel_y"] * k_high_g_accel_multiplier
        df["high_g_accel_z_real"] = df["high_g_accel_z"] * k_high_g_accel_multiplier
        df["baro_pres_avg"] = df[["baro1_pres", "baro2_pres"]].mean(axis=1)
        df["baro_temp_avg"] = df[["baro1_temp", "baro2_temp"]].mean(axis=1)

        # Save to a post-processed CSV
        output_filepath = f"{os.path.splitext(self._offload_data_filepath)[0]}-post.csv"
        df.to_csv(output_filepath)
        return output_filepath


def _select_time_limits(df: pd.DataFrame, timestamp_col: str, altitude_col: str) -> Tuple[float, float]:
    """
    Give plot to user to select time limits.

    :param df: Dataframe to plot from
    :param timestamp_col: Name of column containing timestamp
    :param altitude_col: Name of column containing altitude
    :return: (start_timestamp, end_timestamp)
    """
    df.plot(x=timestamp_col, y=altitude_col)
    plt.title("Altitude over Time - Select 2 Points with Right Click")
    inputs = plt.ginput(n=2, timeout=500, mouse_add=MouseButton.RIGHT, mouse_pop=MouseButton.LEFT)
    plt.close()
    start_time = min(inputs[0][0], inputs[1][0])
    end_time = max(inputs[0][0], inputs[1][0])
    return start_time, end_time


def _graph_data(post_processed_file: str) -> None:
    """
    Produce a number of useful graphs from post-processed data.

    :param post_processed_file: CSV file of post-processed data
    """
    df = pd.read_csv(post_processed_file)
    # IMU data
    fig, ax = plt.subplots(4)
    df.plot(x="timestamp_s", y="baro_pres_avg", ax=ax[0])
    ax[0].set_xlabel("")
    ax[0].set_ylabel("bar")
    df.plot(x="timestamp_s", y="imu_accel_x_avg", ax=ax[1])
    ax[1].set_xlabel("")
    ax[1].set_ylabel("m/s^2")
    df.plot(x="timestamp_s", y="imu_accel_y_avg", ax=ax[2])
    ax[2].set_xlabel("")
    ax[2].set_ylabel("m/s^2")
    df.plot(x="timestamp_s", y="imu_accel_z_avg", ax=ax[3])
    ax[3].set_xlabel("Timestamp (ms)")
    ax[3].set_ylabel("m/s^2")
    # High G Data
    fig2, ax2 = plt.subplots(4)
    df.plot(x="timestamp_s", y="baro_pres_avg", ax=ax2[0])
    ax2[0].set_xlabel("")
    ax2[0].set_ylabel("bar")
    df.plot(x="timestamp_s", y="high_g_accel_x_real", ax=ax2[1])
    ax2[1].set_xlabel("")
    ax2[1].set_ylabel("m/s^2")
    df.plot(x="timestamp_s", y="high_g_accel_y_real", ax=ax2[2])
    ax2[2].set_xlabel("")
    ax2[2].set_ylabel("m/s^2")
    df.plot(x="timestamp_s", y="high_g_accel_z_real", ax=ax2[3])
    ax2[3].set_xlabel("Timestamp (ms)")
    ax2[3].set_ylabel("m/s^2")
    # Baro data
    fig3, ax3 = plt.subplots(1)
    df.plot(x="timestamp_s", y="baro1_pres", ax=ax3)
    df.plot(x="timestamp_s", y="baro2_pres", ax=ax3)
    ax3.set_xlabel("")
    ax3.set_ylabel("bar")
    # df.plot(x="timestamp_s", y="baro_temp_avg", ax=ax3[1])
    # ax3[1].set_xlabel("")
    # ax3[1].set_ylabel("celsius")
    # GPS trajectory
    fig4 = plt.figure()
    ax4 = fig4.add_subplot(111, projection="3d")
    ax4.plot3D(df["gps_lat_mod"], df["gps_long_mod"], df["gps_alt"])
    ax4.set_xlabel("Latitude")
    ax4.set_ylabel("Longitude")
    ax4.set_zlabel("Altitude (m)")
    # State
    fig5, ax5 = plt.subplots(1)
    categories: np.ndarray = np.unique(df["state"])
    cmap = matplotlib.cm.get_cmap("rainbow", len(categories))
    colors = np.linspace(0, 1, len(categories))
    colordict = dict(zip(categories, colors))
    df["Color"] = df["state"].apply(lambda x: cmap(colordict[x]))
    df.plot(
        x="timestamp_s",
        y="pos_z",
        ax=ax5,
        legend=True,
        kind="scatter",
        c=df["Color"],
        s=1,
    )
    ax5.set_xlabel("Timestamp (ms)")
    ax5.set_ylabel("Altitude (m)")
    ax5.set_title("Rocket State")
    # Position and Velocity with marked state transitions
    fig6, ax6 = plt.subplots(2)
    df.plot(x="timestamp_s", y="pos_z", ax=ax6[0])
    ax6[0].set_xlabel("")
    ax6[0].set_ylabel("m")
    df.plot(x="timestamp_s", y="vel_z", ax=ax6[1])
    ax6[1].set_xlabel("")
    ax6[1].set_ylabel("m/s")
    transitions = np.where(df.state[:-1].values != df.state[1:].values)[0]
    vlines = [df.timestamp_s[index] for index in transitions]
    pos_min, pos_max = df["pos_z"].min(), df["pos_z"].max()
    vel_min, vel_max = df["vel_z"].min(), df["vel_z"].max()
    ax6[0].vlines(
        x=vlines,
        ymin=pos_min,
        ymax=pos_max,
        colors="black",
        ls="--",
        lw=1,
        label="state_transitions",
    )
    ax6[1].vlines(
        x=vlines,
        ymin=vel_min,
        ymax=vel_max,
        colors="black",
        ls="--",
        lw=1,
        label="state_transitions",
    )
    if "pyro_status" in df:
        pyro_events = np.where(df.pyro_status[:-1].values != df.pyro_status[1:].values)[0]
        vlines2 = [df.timestamp_s[index] for index in pyro_events]
        ax6[0].vlines(
            x=vlines2,
            ymin=pos_min,
            ymax=pos_max,
            colors="red",
            ls="-",
            lw=1,
            label="pyro_events",
        )
        ax6[1].vlines(
            x=vlines2,
            ymin=vel_min,
            ymax=vel_max,
            colors="red",
            ls="-",
            lw=1,
            label="pyro_events",
        )

    if "acc_z" in df:
        # Z Acceleration and velocity
        fig7, ax7 = plt.subplots(2)
        df.plot(x="timestamp_s", y="acc_z", ax=ax7[0])
        ax7[0].set_xlabel("")
        ax7[0].set_ylabel("m/s^2")
        df.plot(x="timestamp_s", y="vel_z", ax=ax7[1])
        ax7[1].set_xlabel("")
        ax7[1].set_ylabel("m/s")
    plt.show()


if __name__ == "__main__":
    # Set up argument parser
    parser = ArgumentParser(description="Analyze FCB offloaded data via post-processing.")

    read_or_process_group = parser.add_mutually_exclusive_group(required=True)
    read_or_process_group.add_argument(
        "--offload_flight_name",
        type=str,
        help="Perform offload over FCB CLI, saving with given flight name",
    )
    read_or_process_group.add_argument(
        "--process_filepath",
        type=str,
        help="Filepath to CSV of previously offloaded data. Can't be used with --offload_flight_name",
    )
    parser.add_argument(
        "--graph",
        action="store_true",
        help="Graph useful plots from post-processed data",
    )
    args = parser.parse_args()

    if args.offload_flight_name:
        # Get port from user via console
        port_list = SerialPortManager.get_connected_ports()
        port_dev = ConsoleView.request_console_port(port_list=port_list)

        # Set up FCB CLI and run offload
        fcb = FcbCli(
            serial_port=SerialPortManager.get_port(name=port_dev),
        )
        flight_idx: int = ConsoleView.cli_offload_choose_flight(fcb.run_offload_help())
        fcb.run_offload(args.offload_flight_name, flight_idx)

    # Post-process offloaded data
    # Hard coding FCB for now but we might want to make this dynamic in the future
    process_filepath = args.process_filepath if args.process_filepath else os.path.join(FcbCli.OUTPUT_DIR, f"{args.offload_flight_name}-output-FCB.csv")
    analyzer = FcbOffloadAnalyzer(
        offload_data_filepath=process_filepath,
        select_time_limits_cb=_select_time_limits,
    )
    post_processed_filepath = analyzer.analyze()
    if args.graph:
        _graph_data(post_processed_filepath)
