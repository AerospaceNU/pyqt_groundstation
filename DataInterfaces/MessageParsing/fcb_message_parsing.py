import struct
import math
import numpy

from constants import Constants

"""
This file contains functions to parse all the messages coming over serial from the ground station
"""


def lat_lon_decimal_minutes_to_decimal_degrees(min):
    abs_val = abs(min)
    sign = numpy.sign(min)
    return (math.trunc(float(abs_val) / 100.0) + (float(abs_val) % 100.0) / 60.0) * sign


def parse_pyro_continuity_byte(pyro_cont):
    return bin(pyro_cont).lstrip('0b')


def get_fcb_state_from_state_num(state_num):
    if state_num < len(Constants.fcb_state_names):
        return Constants.fcb_state_names[state_num]
    else:
        return Constants.invalid_fcb_state_name


def parse_alt_lat_lon_message(data, dictionary):
    unpacked_data = struct.unpack("<ffffffffIHhbbfbb", data)

    dictionary[Constants.temperature_key] = unpacked_data[0]
    dictionary[Constants.barometer_pressure_key] = unpacked_data[1]
    dictionary[Constants.altitude_key] = unpacked_data[2]
    dictionary[Constants.vertical_speed_key] = unpacked_data[3]
    dictionary[Constants.acceleration_key] = unpacked_data[4]
    dictionary[Constants.latitude_key] = unpacked_data[5]
    dictionary[Constants.longitude_key] = unpacked_data[6]
    dictionary[Constants.gps_alt_key] = unpacked_data[7]
    dictionary[Constants.gps_time_key] = unpacked_data[8]
    dictionary[Constants.ground_speed_key] = unpacked_data[9]
    dictionary[Constants.climb_rate_key] = unpacked_data[10]
    dictionary[Constants.gps_sats_key] = unpacked_data[11]
    dictionary[Constants.pyro_continuity] = parse_pyro_continuity_byte(unpacked_data[12])
    dictionary[Constants.fcb_battery_voltage] = unpacked_data[13]
    dictionary[Constants.fcb_state_key] = get_fcb_state_from_state_num(unpacked_data[14])
    dictionary[Constants.bluetooth_connection_key] = unpacked_data[15]


def parse_ground_station_gps(data, dictionary):
    unpacked_data = struct.unpack("<Bfff", data)

    dictionary[Constants.ground_station_latitude_key] = unpacked_data[1]
    dictionary[Constants.ground_station_longitude_key] = unpacked_data[2]
    dictionary[Constants.ground_station_altitude_key] = unpacked_data[3]


def parse_test_message(data, dictionary):
    """Parses the test message"""
    unpacked_data = struct.unpack("<ffffffdBB", data)

    dictionary[Constants.latitude_key] = lat_lon_decimal_minutes_to_decimal_degrees(unpacked_data[0])
    dictionary[Constants.longitude_key] = lat_lon_decimal_minutes_to_decimal_degrees(unpacked_data[1])
    dictionary[Constants.gps_alt_key] = unpacked_data[2]
    dictionary[Constants.altitude_key] = unpacked_data[3]
    dictionary[Constants.vertical_speed_key] = unpacked_data[4]
    dictionary[Constants.barometer_pressure_key] = unpacked_data[5]
    dictionary[Constants.fcb_battery_voltage] = unpacked_data[6]
    dictionary[Constants.pyro_continuity] = parse_pyro_continuity_byte(unpacked_data[7])
    dictionary[Constants.fcb_state_key] = get_fcb_state_from_state_num(unpacked_data[8])


# Dictionary {[message_number]: [[name], [callback]]}
MESSAGE_CALLBACKS = {0: ["Lat/Lon/Alt", parse_alt_lat_lon_message],
                     2: ["Old transmit stuff", parse_test_message]}


def parse_fcb_message(data):
    """Will check packet type, and call the required parse function"""
    dictionary = {}
    message_number = data[0]

    if message_number in MESSAGE_CALLBACKS:
        # Get CRC, LQI, RSSI data from message (last two bytes)
        fcb_data = data[0:-2]
        radio_data = data[-2:]
        unpacked_radio_status_data = struct.unpack('<bB', radio_data)
        lqi = unpacked_radio_status_data[1] & 0b1111111  # The last 7 bits of the lqi byte are the lqi
        crc = (unpacked_radio_status_data[1] & 0b10000000) # And top is CRC
        crc_str = "Good" if crc else "Bad"

        # Get the packet header
        header_data = fcb_data[0:14]
        unpacked_header = struct.unpack('<BBIBBBBBBBB', header_data)
        dictionary[Constants.software_version_key] = unpacked_header[1]
        dictionary[Constants.timestamp_ms_key] = unpacked_header[2]

        callsign = ""
        for i in range(3, 10):
            if chr(unpacked_header[i]).isalnum():
                callsign += chr(unpacked_header[i])
        dictionary[Constants.callisgn_key] = callsign.strip()

        # Get the rest of the packet
        raw_packet = fcb_data[14:]
        message_type = MESSAGE_CALLBACKS[message_number][0]  # Get message type

        # Parse message
        try:
            MESSAGE_CALLBACKS[message_number][1](raw_packet, dictionary)
            success = True
        except struct.error as e:
            success = False

        # Add radio stuff
        rssi = unpacked_radio_status_data[0]
        if rssi != -128:
            rssi_text = "{} db".format(rssi - 50)
        else:
            rssi_text = "Invalid RSSI"

        dictionary[Constants.rssi_key] = rssi_text
        dictionary[Constants.lqi_key] = lqi
        dictionary[Constants.crc_key] = crc_str

        # TODO this means that the diagonstics tab only shows the most recent _good_ packet. Is that what we want?
        success = success and crc
        return [success, dictionary, message_type]
    elif message_number == 200:  # Ground station packet
        try:
            parse_ground_station_gps(data, dictionary)
            return [True, dictionary, "Ground Station GPS"]
        except:
            return [False, {}, "Ground Station GPS"]
    else:
        return [False, {}, "Invalid message type {}".format(message_number)]
