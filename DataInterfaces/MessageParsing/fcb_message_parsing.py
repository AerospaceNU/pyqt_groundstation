import struct
import math
import numpy

from constants import Constants

"""
This file contains functions to parse all the messages coming over serial from the ground station
"""


def min_to_decimal(min):
    abs_val = abs(min)
    sign = numpy.sign(min)

    return (math.trunc(float(abs_val) / 100.0) + (float(abs_val) % 100.0) / 60.0) * sign


def parse_test_message(data, dictionary):
    """Parses the test message"""
    try:
        unpacked_data = struct.unpack('<BBIBBBBBBBBffffffdBB', data)

        callsign = ""
        for i in range(3, 10):
            callsign += chr(unpacked_data[i])
            print(callsign)

        packet_type = unpacked_data[0]
        dictionary[Constants.software_version_key] = unpacked_data[1]
        dictionary[Constants.timestamp_ms_key] = unpacked_data[2]
        dictionary[Constants.callisgn_key] = callsign.strip()
        dictionary[Constants.latitude_key] = min_to_decimal(unpacked_data[11])
        dictionary[Constants.longitude_key] = min_to_decimal(unpacked_data[12])
        dictionary[Constants.gps_alt_key] = unpacked_data[13]
        dictionary[Constants.altitude_key] = unpacked_data[14]
        dictionary[Constants.vertical_speed_key] = unpacked_data[15]
        dictionary[Constants.barometer_pressure_key] = unpacked_data[16]
        dictionary[Constants.fcb_battery_voltage] = unpacked_data[17]
        dictionary[Constants.pyro_continuity] = unpacked_data[18]
        state_num = unpacked_data[19]

        if state_num < len(Constants.fcb_state_names):
            dictionary[Constants.fcb_state_key] = Constants.fcb_state_names[state_num]
        else:
            dictionary[Constants.fcb_state_key] = Constants.invalid_fcb_state_name

        return True
    except struct.error as e:
        print(e)
        return False


# Dictionary {[message_number]: [[name], [callback]]}
MESSAGE_CALLBACKS = {2: ["Old transmit stuff", parse_test_message]}


def parse_fcb_message(data):
    """Will check packet type, and call the required parse function"""
    dictionary = {}

    message_number = data[0]
    fcb_data = data[0:-2]
    radio_data = data[-2:]
    unpacked_radio = struct.unpack('<BB', radio_data)
    lqi = unpacked_radio[1] << 1  # The last 7 bits of the lqi byte are the lqi

    if message_number in MESSAGE_CALLBACKS:
        message_type = MESSAGE_CALLBACKS[message_number][0]  # Get message type
        success = MESSAGE_CALLBACKS[message_number][1](fcb_data, dictionary)  # Parse message

        # Add radio stuff
        dictionary[Constants.rssi_key] = unpacked_radio[0]
        dictionary[Constants.lqi_key] = lqi

        # return
        return [success, dictionary, message_type]
    else:
        return [False, {}, "Invalid message type {}".format(message_number)]
