"""Handles all behavior related to serial port use and management"""

from typing import List, Optional

import serial
import serial.tools.list_ports

from src.exceptions import SerialPortDisconnectedError


class SerialPort:
    """Manages a single serial port and access to it"""

    _DEFAULT_BAUD_RATE = 9600
    _DEFAULT_PORT_TIMEOUT_S = 1

    def __init__(self, name: str) -> None:
        """
        Initialize a serial port with the given name

        :param name: Name of serial port to initialize
        """
        self.name: str = name
        self.connected: bool = False
        self._port: serial.Serial = serial.Serial(
            port=name,
            baudrate=self._DEFAULT_BAUD_RATE,
            timeout=self._DEFAULT_PORT_TIMEOUT_S,
        )

    def write(self, data: bytes) -> None:
        """
        Write data to serial port.

        :param data: Bytes to write to serial port
        """
        try:
            self._port.write(data)
        except Exception:
            raise SerialPortDisconnectedError(port_name=self.name)

    def read(self, size: int = 2048) -> Optional[bytes]:
        """
        Read a number of bytes from the serial port

        :param size: Number of bytes to read from port
        """
        try:
            data: Optional[bytes] = self._port.read(size)
        except Exception:
            raise SerialPortDisconnectedError(port_name=self.name)
        return data


class SerialPortManager:
    """Manages all serial ports"""

    _serial_ports: List[SerialPort] = []

    @classmethod
    def _serial_port_names(cls) -> List[str]:
        return [port.name for port in cls._serial_ports]

    @classmethod
    def _update_connected_ports(cls) -> None:
        connected_ports = [
            port_info.device for port_info in serial.tools.list_ports.comports()
        ]
        for port_name in connected_ports:
            if port_name not in cls._serial_port_names():
                cls._serial_ports.append(SerialPort(name=port_name))
        for port in cls._serial_ports:
            port.connected = port.name in connected_ports

    @classmethod
    def get_connected_ports(cls) -> List[str]:
        """
        Update list of connected serial ports and return

        :return: Currently connected serial ports
        """
        cls._update_connected_ports()
        return [port.name for port in cls._serial_ports if port.connected]

    @classmethod
    def get_port(cls, name: str) -> SerialPort:
        """
        Get serial port associated with given name

        :param name: Name of serial port
        :return: SerialPort object associated with the given port name
        """
        if name not in cls._serial_port_names():
            cls._serial_ports.append(SerialPort(name=name))
        cls._update_connected_ports()
        return cls._serial_ports[cls._serial_port_names().index(name)]
