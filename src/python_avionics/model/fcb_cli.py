"""Handles all FCB-related communication tasks and initial processing of those tasks"""
import csv
import os
import shlex
import struct
import sys
import time
from argparse import ArgumentParser
from collections import namedtuple
from typing import Any, List

import pandas as pd

from src.python_avionics.exceptions import FcbIncompleteError, FcbNoAckError
from src.python_avionics.model.serial_port import SerialPort, SerialPortManager
from src.python_avionics.view.console_view import ConsoleView

UnpackProperty = namedtuple("UnpackProperty", "name unpack_str")
PackProperty = namedtuple("PackProperty", "name pack_str")


class FcbCli:
    """Controls raw reading and writing to FCB command line via commands."""

    _ACK = "\r\nOK\r\n"
    _COMPLETE = "\r\nDONE\r\n\r\n"
    _HELP_COMMAND = "--help"
    _OFFLOAD_HELP_COMMAND = "--offload -h"
    _OFFLOAD_FLIGHT_COMMAND = "--offload -f {flight_num}"
    _SIM_COMMAND = "--sim"
    _SENSE_COMMAND = "--sense"
    _SHUTDOWN_COMMAND = "--shutdown"
    _ERASE_FLASH_COMMAND = "--erase"

    OUTPUT_DIR = "output"

    LOG_TYPES = ["FCB", "LINECUTTER"]

    def __init__(self, serial_port: SerialPort):
        """
        Initialize an FCB instance.

        :param serial_port: Serial port to use to communicate with FCB CLI
        """
        self.serial_port = serial_port

    def _read_ack(self) -> bool:
        """
        Read acknowledgement from FCB.

        :return: Whether acknowledgement was found or not
        """
        rx_data = self.serial_port.read(size=len(self._ACK))
        if rx_data is None:
            return False
        return rx_data.decode("utf-8") == self._ACK

    def _has_complete(self, search_str: str) -> bool:
        """
        Return whether given string ends with complete identifier

        :param search_str: String to search
        :return: Whether complete identifier was found
        """
        return search_str.endswith(self._COMPLETE)

    def run_command(self, command: str) -> Any:
        """
        Runs command for FCB CLI given a string.

        The given command will be run on the FCB, but additional processing occurs
        here both before and after the command is sent.

        :param command: Command to run as space-separated string
        :return: Return value from command, or None if no command matched
        """
        # Set up complete argument parser
        command_parser = ArgumentParser(prog="fcb_cli", description="Python FCB CLI arguments")
        subparsers = command_parser.add_subparsers(help="FCB CLI help", dest="command")

        # Add subparsers as options

        subparsers.add_parser("help", help="Standard command line help string from FCB")

        offload_parser = subparsers.add_parser("offload", help="Offload data from FCB")
        offload_parser.add_argument(
            "--flight_name",
            type=str,
            required=False,
            help="Name of flight, used for saving",
        )
        offload_parser.add_argument(
            "--flight_num",
            type=int,
            required=False,
            help="Flight number to offload",
        )
        offload_parser.add_argument(
            "--list",
            required=False,
            action="store_true",
            help="Dump a list of all flights stored",
        )

        sim_parser = subparsers.add_parser("sim", help="Sim flight to FCB")
        sim_parser.add_argument(
            "--flight_file",
            type=str,
            required=True,
            help="CSV file of flight to simulate",
        )

        subparsers.add_parser("sense", help="Reads back most recent sensor data")

        subparsers.add_parser(
            "shutdown",
            help="Prevent FCB from doing anything else. FCB won't actually shut off, " "but it won't do or respond to anything",
        )

        subparsers.add_parser(
            "erase",
            help="Erases entire FCB flash",
        )

        # Parse arguments
        commands = shlex.split(command, posix=False)
        parsed_args, commands = command_parser.parse_known_args(commands)

        # Run appropriate function based on given command and arguments
        if parsed_args.command == "help":
            return self.run_help()
        if parsed_args.command == "offload":
            if parsed_args.list:
                return self.run_offload_help()
            else:
                self.run_offload(
                    flight_name=parsed_args.flight_name,
                    flight_num=parsed_args.flight_num,
                )
            return "Success"
        if parsed_args.command == "sense":
            return self.run_sense()
        if parsed_args.command == "sim":
            self.run_sim(flight_filepath=parsed_args.flight_file.strip('"'))
            return "Success"
        if parsed_args.command == "shutdown":
            self.run_shutdown()
            return "Success"
        if parsed_args.command == "erase":
            self.run_erase()
            return "Success"
        else:
            return "Failed. Invalid Command"

    @staticmethod
    def _linebreak(string: str) -> str:
        """
        Add line break to a string by appending new line character.

        :param string: String to append to
        :return: Given string with new line character at end
        """
        return f"{string}\n"

    def run_help(self) -> str:
        """
        Get help string from FCB.

        :return: Help string
        """
        self.serial_port.write(self._linebreak(self._HELP_COMMAND).encode("utf-8"))
        if not self._read_ack():
            raise FcbNoAckError(fcb_command=self._HELP_COMMAND)
        help_bytes = self.serial_port.read(size=10000)
        help_str = "" if not help_bytes else help_bytes.decode("utf-8")
        if not self._has_complete(search_str=help_str):
            raise FcbIncompleteError(fcb_command=self._HELP_COMMAND)
        return help_str.strip(self._COMPLETE)

    def run_offload_help(self) -> str:
        self.serial_port.write(self._linebreak(self._OFFLOAD_HELP_COMMAND).encode("utf-8"))
        if not self._read_ack():
            raise FcbNoAckError(fcb_command=self._OFFLOAD_HELP_COMMAND)
        help_bytes = self.serial_port.read(size=10000)
        help_str = "" if not help_bytes else help_bytes.decode("utf-8")
        if not self._has_complete(search_str=help_str):
            raise FcbIncompleteError(fcb_command=self._OFFLOAD_HELP_COMMAND)
        help_str = help_str.strip(self._COMPLETE)
        return help_str

    def run_offload(self, flight_name: str, flight_num: int) -> None:
        """
        Manage data offload on the FCB.

        :param flight_name: Name of flight, used in saving output
        :param flight_num: Flight number as reported by FCB in run_offload_help
        """

        # Start offloading provided flight number
        self.serial_port.write(self._linebreak(self._OFFLOAD_FLIGHT_COMMAND.format(flight_num=flight_num)).encode("utf-8"))
        if not self._read_ack():
            raise FcbNoAckError(fcb_command=self._OFFLOAD_FLIGHT_COMMAND)

        # Offload into output binary file
        if not os.path.isdir("output"):
            os.makedirs("output")
        output_bin_filepath = os.path.join("output", f"{flight_name}-output.bin")
        if os.path.isfile(output_bin_filepath):
            raise FileExistsError(output_bin_filepath)
        k_read_size = 2048
        with open(output_bin_filepath, "wb") as output_bin_file:
            while True:
                byte_array = self.serial_port.read(size=k_read_size)
                if not byte_array:
                    raise FcbIncompleteError(fcb_command=self._OFFLOAD_FLIGHT_COMMAND)
                output_bin_file.write(byte_array)
                if len(byte_array) < k_read_size:
                    break

        # Ensure offload is complete. Must read here since complete message could be
        # split between the last two reads
        with open(output_bin_filepath, "rb") as output_bin_file:
            output_bin_file.seek(-len(self._COMPLETE), os.SEEK_END)
            complete_str = output_bin_file.read().decode("utf-8")
        if complete_str != self._COMPLETE:
            raise FcbIncompleteError(fcb_command=self._OFFLOAD_FLIGHT_COMMAND)

        # Open and read binary file line by line, saving to csvs

        output_csv_filepaths = [os.path.join("output", f"{flight_name}-output-{log_type}.csv") for log_type in self.LOG_TYPES]
        for filepath in output_csv_filepaths:
            if os.path.isfile(filepath):
                raise FileExistsError(filepath)
        input_bin_file = open(output_bin_filepath, "rb")
        output_csv_files = [open(filepath, "w", newline="") for filepath in output_csv_filepaths]
        csv_writers = [csv.writer(csv_file) for csv_file in output_csv_files]
        log_struct_strs: List[str] = ["" for _ in self.LOG_TYPES]
        log_struct_sizes: List[int] = [0 for _ in self.LOG_TYPES]
        for i, _ in enumerate(self.LOG_TYPES):
            csv_writers[i].writerow([prop.name for prop in self._log_data_struct[i]])
            log_struct_strs[i] = f"<{''.join([prop.unpack_str for prop in self._log_data_struct[i]])}"
            log_struct_sizes[i] = struct.Struct(log_struct_strs[i]).size
        log_struct_full_size = max(log_struct_sizes)
        while True:
            packed_data = input_bin_file.read(log_struct_full_size)
            try:
                packet_type = int(packed_data[0])
                unpacked_data = struct.unpack(log_struct_strs[packet_type], packed_data[0 : log_struct_sizes[packet_type]])
            except struct.error:
                break
            except IndexError:
                break  # Packet type invalid
            # Only keep things if timestamp isn't 0xFF
            if unpacked_data[1] < (2 << 32) - 1:
                csv_writers[packet_type].writerow(unpacked_data)

    def run_erase(self) -> None:
        """
        Erases FCB flash
        """
        self.serial_port.write(self._linebreak(self._ERASE_FLASH_COMMAND).encode("utf-8"))
        if not self._read_ack():
            raise FcbNoAckError(fcb_command=self._ERASE_FLASH_COMMAND)
        help_bytes = self.serial_port.read(size=10000)
        help_str = "" if not help_bytes else help_bytes.decode("utf-8")
        # Read from FCB once per second until complete msg is read
        while not self._has_complete(search_str=help_str):
            if not help_bytes:
                raise FcbIncompleteError(fcb_command=self._ERASE_FLASH_COMMAND)
            ConsoleView.cli_erase_print(help_str)
            help_bytes = self.serial_port.read(size=10000)
            help_str = "" if not help_bytes else help_bytes.decode("utf-8")

    def run_sim(self, flight_filepath: str) -> None:
        """
        Run flight simulation for the FCB by providing data from flight file

        :param flight_filepath: Filepath to the flight to read through for sim
        """
        k_min_code_loop_period_s = 0.02

        # Read CSV to ensure flight filepath is valid
        df = pd.read_csv(flight_filepath, index_col=0)

        # Start sim
        self.serial_port.write(self._linebreak(self._SIM_COMMAND).encode("utf-8"))
        if not self._read_ack():
            raise FcbNoAckError(fcb_command=self._SIM_COMMAND)

        # Start sending sim data
        df["time_diff"] = df["timestamp_s"].diff().fillna(0)
        for row in df.itertuples():
            # Wait for next transmit time
            time_to_wait = max(k_min_code_loop_period_s, row.time_diff / 1000.0)
            time.sleep(time_to_wait)
            data = struct.pack(
                self._sensor_data_struct_str,
                row.timestamp_s,
                row.timestamp_ms,
                row.imu1_accel_x,
                row.imu1_accel_y,
                row.imu1_accel_z,
                row.imu1_accel_x_real,
                row.imu1_accel_y_real,
                row.imu1_accel_z_real,
                row.imu1_gyro_x,
                row.imu1_gyro_y,
                row.imu1_gyro_z,
                row.imu1_gyro_x_real,
                row.imu1_gyro_y_real,
                row.imu1_gyro_z_real,
                row.imu1_mag_x,
                row.imu1_mag_y,
                row.imu1_mag_z,
                row.imu1_mag_x_real,
                row.imu1_mag_y_real,
                row.imu1_mag_z_real,
                row.imu2_accel_x,
                row.imu2_accel_y,
                row.imu2_accel_z,
                row.imu2_accel_x_real,
                row.imu2_accel_y_real,
                row.imu2_accel_z_real,
                row.imu2_gyro_x,
                row.imu2_gyro_y,
                row.imu2_gyro_z,
                row.imu2_gyro_x_real,
                row.imu2_gyro_y_real,
                row.imu2_gyro_z_real,
                row.imu2_mag_x,
                row.imu2_mag_y,
                row.imu2_mag_z,
                row.imu2_mag_x_real,
                row.imu2_mag_y_real,
                row.imu2_mag_z_real,
                row.high_g_accel_x,
                row.high_g_accel_y,
                row.high_g_accel_z,
                row.high_g_accel_x_real,
                row.high_g_accel_y_real,
                row.high_g_accel_z_real,
                row.baro1_temp,
                row.baro1_pres,
                row.baro2_temp,
                row.baro2_pres,
                row.gps_lat,
                row.gps_long,
                row.gps_alt,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                "a".encode("utf-8"),
                row.battery_voltage,
                row.pyro_cont,
                row.pyro_cont >> 1,
                row.pyro_cont >> 2,
                row.pyro_cont >> 3,
                row.pyro_cont >> 4,
                row.pyro_cont >> 5,
            )
            # Send data over serial
            self.serial_port.write(data)

        # Check for complete ACK
        complete_data = self.serial_port.read(size=len(self._COMPLETE))
        if not complete_data:
            raise FcbIncompleteError(fcb_command=self._SIM_COMMAND)
        if not self._has_complete(search_str=complete_data.decode("utf8")):
            raise FcbIncompleteError(fcb_command=self._SIM_COMMAND)

    def run_sense(self) -> str:
        """
        Get sense string from FCB.

        :return: Sense string
        """
        self.serial_port.write(self._linebreak(self._SENSE_COMMAND).encode("utf-8"))
        if not self._read_ack():
            raise FcbNoAckError(fcb_command=self._SENSE_COMMAND)
        sense_bytes = self.serial_port.read(size=10000)
        sense_str = "" if not sense_bytes else sense_bytes.decode("utf-8")
        if not self._has_complete(search_str=sense_str):
            raise FcbIncompleteError(fcb_command=self._SENSE_COMMAND)
        return sense_str.strip(self._COMPLETE)

    def run_shutdown(self) -> None:
        """
        Prevent FCB from doing anything else.

        FCB won't actually shut off, but it won't do or respond to anything.
        """
        self.serial_port.write(self._linebreak(self._SHUTDOWN_COMMAND).encode("utf-8"))
        if not self._read_ack():
            raise FcbNoAckError(fcb_command=self._SHUTDOWN_COMMAND)
        rx_bytes = self.serial_port.read(size=10000)
        rx_str = "" if not rx_bytes else rx_bytes.decode("utf-8")
        if not self._has_complete(search_str=rx_str):
            raise FcbIncompleteError(fcb_command=self._SHUTDOWN_COMMAND)

    @property
    def _sensor_data_struct_str(self) -> str:
        """
        Get FCB sensor data properties as a struct string representation.

        :return: Struct-compatible string
        """
        pack_properties = [
            PackProperty("timestamp_s", "L"),
            PackProperty("timestamp_us", "L"),
            PackProperty("imu1_accel_x_raw", "h"),
            PackProperty("imu1_accel_y_raw", "h"),
            PackProperty("imu1_accel_z_raw", "h"),
            PackProperty("imu1_accel_x", "d"),
            PackProperty("imu1_accel_y", "d"),
            PackProperty("imu1_accel_z", "d"),
            PackProperty("imu1_gyro_x_raw", "h"),
            PackProperty("imu1_gyro_y_raw", "h"),
            PackProperty("imu1_gyro_z_raw", "h"),
            PackProperty("imu1_gyro_x", "d"),
            PackProperty("imu1_gyro_y", "d"),
            PackProperty("imu1_gyro_z", "d"),
            PackProperty("imu1_mag_x_raw", "h"),
            PackProperty("imu1_mag_y_raw", "h"),
            PackProperty("imu1_mag_z_raw", "h"),
            PackProperty("imu1_mag_x", "d"),
            PackProperty("imu1_mag_y", "d"),
            PackProperty("imu1_mag_z", "d"),
            PackProperty("imu2_accel_x_raw", "h"),
            PackProperty("imu2_accel_y_raw", "h"),
            PackProperty("imu2_accel_z_raw", "h"),
            PackProperty("imu2_accel_x", "d"),
            PackProperty("imu2_accel_y", "d"),
            PackProperty("imu2_accel_z", "d"),
            PackProperty("imu2_gyro_x_raw", "h"),
            PackProperty("imu2_gyro_y_raw", "h"),
            PackProperty("imu2_gyro_z_raw", "h"),
            PackProperty("imu2_gyro_x", "d"),
            PackProperty("imu2_gyro_y", "d"),
            PackProperty("imu2_gyro_z", "d"),
            PackProperty("imu2_mag_x_raw", "h"),
            PackProperty("imu2_mag_y_raw", "h"),
            PackProperty("imu2_mag_z_raw", "h"),
            PackProperty("imu2_mag_x", "d"),
            PackProperty("imu2_mag_y", "d"),
            PackProperty("imu2_mag_z", "d"),
            PackProperty("high_g_accel_x_raw", "h"),
            PackProperty("high_g_accel_y_raw", "h"),
            PackProperty("high_g_accel_z_raw", "h"),
            PackProperty("high_g_accel_x", "d"),
            PackProperty("high_g_accel_y", "d"),
            PackProperty("high_g_accel_z", "d"),
            PackProperty("baro1_temp", "d"),
            PackProperty("baro1_pres", "d"),
            PackProperty("baro2_temp", "d"),
            PackProperty("baro2_pres", "d"),
            PackProperty("gps_lat", "f"),
            PackProperty("gps_long", "f"),
            PackProperty("gps_alt", "f"),
            PackProperty("gps_speed", "f"),
            PackProperty("gps_course", "f"),
            PackProperty("gps_latitude_deviation", "f"),
            PackProperty("gps_longitude_deviation", "f"),
            PackProperty("gps_altitude_deviation", "f"),
            PackProperty("gps_speed_kph", "f"),
            PackProperty("gps_speed_knots", "f"),
            PackProperty("gps_timestamp", "Q"),
            PackProperty("gps_seconds", "i"),
            PackProperty("gps_microseconds", "i"),
            PackProperty("gps_minutes", "i"),
            PackProperty("gps_hours", "i"),
            PackProperty("gps_day", "i"),
            PackProperty("gps_month", "i"),
            PackProperty("gps_year", "i"),
            PackProperty("gps_num_sats", "i"),
            PackProperty("gps_status", "c"),
            PackProperty("battery_voltage", "d"),
            PackProperty("pyro_continuity", "??????"),
        ]
        # Struct unpack string starts with < for little endian
        struct_pack_str = f"<{''.join([prop.pack_str for prop in pack_properties])}"
        return struct_pack_str

    @property
    def _log_data_struct(self) -> List[List[UnpackProperty]]:
        """
        Get FCB log data properties as a struct string representation.

        :return: List of list of log data structs, one for each log type
        """

        # FCB Data
        unpack_properties: List[List[UnpackProperty]] = [
            [  # FCB Data
                UnpackProperty("packetType", "B"),
                UnpackProperty("timestamp_s", "I"),
                UnpackProperty("timestamp_ms", "I"),
                UnpackProperty("imu1_accel_x", "h"),
                UnpackProperty("imu1_accel_y", "h"),
                UnpackProperty("imu1_accel_z", "h"),
                UnpackProperty("imu1_gyro_x", "h"),
                UnpackProperty("imu1_gyro_y", "h"),
                UnpackProperty("imu1_gyro_z", "h"),
                UnpackProperty("imu1_mag_x", "h"),
                UnpackProperty("imu1_mag_y", "h"),
                UnpackProperty("imu1_mag_z", "h"),
                UnpackProperty("imu2_accel_x", "h"),
                UnpackProperty("imu2_accel_y", "h"),
                UnpackProperty("imu2_accel_z", "h"),
                UnpackProperty("imu2_gyro_x", "h"),
                UnpackProperty("imu2_gyro_y", "h"),
                UnpackProperty("imu2_gyro_z", "h"),
                UnpackProperty("imu2_mag_x", "h"),
                UnpackProperty("imu2_mag_y", "h"),
                UnpackProperty("imu2_mag_z", "h"),
                UnpackProperty("high_g_accel_x", "h"),
                UnpackProperty("high_g_accel_y", "h"),
                UnpackProperty("high_g_accel_z", "h"),
                UnpackProperty("baro1_temp", "d"),
                UnpackProperty("baro1_pres", "d"),
                UnpackProperty("baro2_temp", "d"),
                UnpackProperty("baro2_pres", "d"),
                UnpackProperty("gps_lat", "f"),
                UnpackProperty("gps_long", "f"),
                UnpackProperty("gps_alt", "f"),
                UnpackProperty("battery_voltage", "d"),
                UnpackProperty("pyro_cont", "B"),
                UnpackProperty("pyro_status", "B"),
                UnpackProperty("heading", "d"),
                UnpackProperty("vtg", "d"),
                UnpackProperty("pos_x", "d"),
                UnpackProperty("pos_y", "d"),
                UnpackProperty("pos_z", "d"),
                UnpackProperty("vel_x", "d"),
                UnpackProperty("vel_y", "d"),
                UnpackProperty("vel_z", "d"),
                UnpackProperty("acc_x", "d"),
                UnpackProperty("acc_y", "d"),
                UnpackProperty("acc_z", "d"),
                UnpackProperty("q_x", "d"),
                UnpackProperty("q_y", "d"),
                UnpackProperty("q_z", "d"),
                UnpackProperty("q_w", "d"),
                UnpackProperty("state", "B"),
            ],
            [  # Line Cutter Data
                UnpackProperty("packetType", "B"),
                UnpackProperty("timestamp_s", "I"),
                UnpackProperty("timestamp_ms", "I"),
                UnpackProperty("lineCutterNumber", "B"),
                UnpackProperty("state", "B"),
                UnpackProperty("timestamp", "I"),
                UnpackProperty("pressure", "I"),
                UnpackProperty("altitude", "f"),
                UnpackProperty("deltaAltitude", "f"),
                UnpackProperty("temperature", "f"),
                UnpackProperty("accelNorm", "f"),
                UnpackProperty("battery", "f"),
                UnpackProperty("cutSense1", "H"),
                UnpackProperty("cutSense2", "H"),
                UnpackProperty("currentSense", "H"),
                UnpackProperty("photoresistor", "H"),
            ],
        ]
        return unpack_properties


if __name__ == "__main__":
    # Get port from user via console
    port_list = SerialPortManager.get_connected_ports()
    port_dev = ConsoleView.request_console_port(port_list=port_list)

    # Set up FCB CLI and run commands from command line
    fcb = FcbCli(
        serial_port=SerialPortManager.get_port(name=port_dev),
    )
    passed_args = [f'"{arg}"' if " " in arg else arg for arg in sys.argv[1:]]
    print(fcb.run_command(" ".join(passed_args)))
