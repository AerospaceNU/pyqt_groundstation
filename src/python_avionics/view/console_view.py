"""
Manages all user interaction with the console used across multiple scripts.

This has significant less responsibility than GUIs because the ConsoleView doesn't need to initiate functions
in the backend. It just takes requests from the backend and processes them, typically as a callback.
"""
from typing import List


class ConsoleView:
    """Manages all user interaction with the console."""

    @staticmethod
    def request_console_port(port_list: List[str]) -> str:
        """
        Request a serial port from the user over the console.

        :param port_list: List of ports user can pick from
        :return: Port chosen
        """
        if len(port_list) == 0:
            print("No available ports, exiting")
            exit(-1)
        elif len(port_list) == 1:
            return port_list[0]
        for port in port_list:
            print(port)
        while True:
            port_dev = input("Enter port name to connect to: ")
            if port_dev not in port_list:
                print("Invalid entered port")
                continue
            break
        return port_dev

    @staticmethod
    def cli_offload_choose_flight(offload_help_str: str) -> int:
        """
        Choose a flight from command line given an offload help string.

        :param offload_help_str: String used to help user pick flight
        :return: Flight chosen
        """
        # Ask user for input
        print(offload_help_str)
        while True:
            flight_num_str = input("Enter Flight Num: ")
            try:
                flight_num = int(flight_num_str)
                break
            except ValueError:
                print("Invalid flight number entered")
        return flight_num

    @staticmethod
    def cli_erase_print(erase_help_str: str) -> None:
        """
        Print erase msg

        :param offload_help_str: String used to check erase status
        :return: Nothing
        """
        print(erase_help_str)
