"""
This file provides functions to create binary messages to send to the ground station
"""

import datetime
import math
import struct

import numpy

from src.constants import Constants


def createRadioBandCommandMessage(destination, target_radio, channel):
    return struct.pack("<BHBBb", destination, 3, 1, target_radio, channel)  # destination, length, command id, target radio, channel


def createCLICommandMessage(destination, command: str):
    command = command.strip() + "\n"
    command_bytes = command.encode()
    return struct.pack("<BH", destination, len(command_bytes)) + command_bytes
