import struct
import math
import numpy

from constants import Constants

"""
This file contains functions to parse all the messages coming over serial from the ground station
"""


def quaternion_to_euler_angle(w, x, y, z):
    """Copied from stack overflow"""

    ysqr = y * y

    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + ysqr)
    X = math.degrees(math.atan2(t0, t1))

    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    Y = math.degrees(math.asin(t2))

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (ysqr + z * z)
    Z = math.degrees(math.atan2(t3, t4))

    return [X, Y, Z]


def compass_heading_deg_to_enu_rad(heading):
    return -math.radians(heading - 90)


def lat_lon_decimal_minutes_to_decimal_degrees(min):
    """
    FCB data comes in as ddmm.mmmmmm
    This converts to dd.dddddddd
    """
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


def parse_orientation_message(data, dictionary):
    """uint8 state, float qw, qx, qy, qz, wx, wy, wz, ax, ay, az, bx, by, bz;"""
    unpacked_data = struct.unpack("<Bfffffffffffff", data)

    dictionary[Constants.fcb_state_key] = get_fcb_state_from_state_num(unpacked_data[0])

    qw = unpacked_data[1]  # Orientation
    qx = unpacked_data[2]
    qy = unpacked_data[3]
    qz = unpacked_data[4]
    wx = unpacked_data[5]  # Rotational velocity
    wy = unpacked_data[6]
    wz = unpacked_data[7]
    ax = unpacked_data[8]  # Acceleration
    ay = unpacked_data[9]
    az = unpacked_data[10]
    bx = unpacked_data[11]  # Magnetic field
    by = unpacked_data[12]
    bz = unpacked_data[13]

    dictionary[Constants.orientation_quaternion_key] = [qw, qx, qy, qz]
    dictionary[Constants.orientation_rpy_key] = quaternion_to_euler_angle(qw, qx, qy, qz)
    dictionary[Constants.rotational_velocity_key] = [wx, wy, wz]
    dictionary[Constants.acceleration_key] = [ax, ay, az]
    dictionary[Constants.magnetic_vector_key] = [bx, by, bz]


def parse_position_data_message(data, dictionary):
    unpacked_data = struct.unpack("<fffffffffIBBBB", data)

    dictionary[Constants.temperature_key] = unpacked_data[0]
    dictionary[Constants.altitude_key] = unpacked_data[1]
    dictionary[Constants.vertical_speed_key] = unpacked_data[2]
    dictionary[Constants.latitude_key] = unpacked_data[3]
    dictionary[Constants.longitude_key] = unpacked_data[4]
    dictionary[Constants.gps_alt_key] = unpacked_data[5]
    dictionary[Constants.fcb_battery_voltage] = unpacked_data[6]
    dictionary[Constants.ground_speed_key] = unpacked_data[7] * 0.514444  # fcb reports speed in kts
    dictionary[Constants.course_over_ground_key] = compass_heading_deg_to_enu_rad(unpacked_data[8])  # GPS reports compass heading (NED and degrees)
    dictionary[Constants.gps_time_key] = unpacked_data[9]
    dictionary[Constants.gps_sats_key] = unpacked_data[10]
    dictionary[Constants.pyro_continuity] = parse_pyro_continuity_byte(unpacked_data[11])
    dictionary[Constants.fcb_state_key] = get_fcb_state_from_state_num(unpacked_data[12])
    dictionary[Constants.bluetooth_connection_key] = unpacked_data[13]  # TODO: Parse this better


def parse_ground_station_gps(data, dictionary):
    unpacked_data = struct.unpack("<Bfffdd", data)

    dictionary[Constants.ground_station_latitude_key] = lat_lon_decimal_minutes_to_decimal_degrees(unpacked_data[1])
    dictionary[Constants.ground_station_longitude_key] = lat_lon_decimal_minutes_to_decimal_degrees(unpacked_data[2])
    dictionary[Constants.ground_station_altitude_key] = unpacked_data[3]
    dictionary[Constants.ground_station_pressure_key] = unpacked_data[4]
    dictionary[Constants.ground_station_temperature_key] = unpacked_data[5]


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
MESSAGE_CALLBACKS = {2: ["Orientation", parse_orientation_message],
                     3: ["Position Data", parse_position_data_message],
                     }
# -1: ["Old transmit stuff", parse_test_message]} #Not used anymore

GROUND_STATION_MESSAGE_TYPES = ["Ground Station GPS"]


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
        crc = (unpacked_radio_status_data[1] & 0b10000000)  # And top is CRC
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

        return [success, dictionary, message_type, crc]
    elif message_number == 200:  # Ground station packet
        try:
            data = data[0:29]
            parse_ground_station_gps(data, dictionary)
            return [True, dictionary, GROUND_STATION_MESSAGE_TYPES[0], 1]
        except:
            return [False, {}, GROUND_STATION_MESSAGE_TYPES[0], 1]
    else:
        return [False, {}, "Invalid message type {}".format(message_number), 1]


def is_ground_station_message(message_type):
    return message_type in GROUND_STATION_MESSAGE_TYPES
