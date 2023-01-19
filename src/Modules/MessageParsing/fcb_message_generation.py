"""
This file provides functions to create binary messages to send to the ground station
"""

import struct

packet_num = 0


def createRadioBandCommandMessage(destination, target_radio, channel):
    return struct.pack("<BHBBb", destination, 3, 1, target_radio, channel)  # destination, length, command id, target radio, channel


def createCLICommandMessage(destination, command: str):
    command = command.strip() + "\n"
    command_bytes = command.encode()
    return struct.pack("<BH", destination, len(command_bytes)) + command_bytes


def createRadioPacket(packet_type, payload: bytes):
    payload_len = len(payload)
    print(payload_len)

    return struct.pack(f"<BBBI8s{payload_len}s", packet_type, 0, 1, 2, "callsign".encode(), payload)  # Callsign needs to be 8 charecters long


def createCLICommandPacket(payload: str):
    global packet_num

    payload_bytes = payload.encode()
    payload_len = len(payload_bytes)
    full_payload = struct.pack(f"<BB{payload_len}s", payload_len, packet_num, payload_bytes)

    packet_num += 1
    if packet_num > 255:
        packet_num = 0

    return createRadioPacket(5, full_payload)
