import struct
import math
import numpy
import datetime

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
    pyro_list = []
    for i in range(Constants.MAX_PYROS):
        has_cont_b = (pyro_cont & 1 << i) > 0
        pyro_list.append(has_cont_b)

    return pyro_list


def get_fcb_state_from_state_num(state_num):
    if state_num < len(Constants.fcb_state_names):
        return Constants.fcb_state_names[state_num]
    else:
        return Constants.invalid_fcb_state_name


def parse_orientation_message(data, dictionary):
    """uint8 state, int8 qw, qx, qy, qz, float wx, wy, wz, ax, ay, az, bx, by, bz;"""
    data = data[0:41]
    unpacked_data = struct.unpack("<Bbbbbfffffffff", data)
    print(unpacked_data)

    dictionary[Constants.fcb_state_key] = get_fcb_state_from_state_num(unpacked_data[0])

    qw = unpacked_data[1] / 100.0  # Orientation, [-100, 100x]
    qx = unpacked_data[2] / 100.0
    qy = unpacked_data[3] / 100.0
    qz = unpacked_data[4] / 100.0
    wx = unpacked_data[5]  # Rotational velocity
    wy = unpacked_data[6]
    wz = unpacked_data[7]
    ax = unpacked_data[8]  # Acceleration
    ay = unpacked_data[9]
    az = unpacked_data[10]
    bx = unpacked_data[11]  # Magnetic field
    by = unpacked_data[12]
    bz = unpacked_data[13]

    rpy = quaternion_to_euler_angle(qw, qx, qy, qz)

    dictionary[Constants.roll_position_key] = rpy[0]
    dictionary[Constants.pitch_position_key] = rpy[1]
    dictionary[Constants.yaw_position_key] = rpy[2]

    dictionary[Constants.rotational_velocity_x_key] = wx
    dictionary[Constants.rotational_velocity_y_key] = wy
    dictionary[Constants.rotational_velocity_z_key] = wz

    dictionary[Constants.acceleration_x_key] = ax
    dictionary[Constants.acceleration_y_key] = ay
    dictionary[Constants.acceleration_z_key] = az

    dictionary[Constants.magnetometer_x_key] = bx
    dictionary[Constants.magnetometer_y_key] = by
    dictionary[Constants.magnetometer_z_key] = bz

    dictionary[Constants.orientation_quaternion_key] = [qw, qx, qy, qz]
    dictionary[Constants.orientation_rpy_key] = rpy
    dictionary[Constants.rotational_velocity_key] = [wx, wy, wz]
    dictionary[Constants.acceleration_vector_key] = [ax, ay, az]
    dictionary[Constants.magnetic_vector_key] = [bx, by, bz]


def parse_altitude_info(data, dictionary):
    data = data[0:24]
    unpacked_data = struct.unpack("<ffffff", data)
    dictionary[Constants.press1_key] = unpacked_data[0]
    dictionary[Constants.press2_key] = unpacked_data[1]
    dictionary[Constants.press_ref_key] = unpacked_data[2]
    dictionary[Constants.ground_elevation_key] = unpacked_data[3]
    dictionary[Constants.ground_temp_key] = unpacked_data[4]
    dictionary[Constants.main_cut_alt_key] = unpacked_data[5]


def parse_position_data_message(data, dictionary):
    data = data[0:44]
    unpacked_data = struct.unpack("<fffffffffIBBBB", data)

    dictionary[Constants.temperature_key] = unpacked_data[0]
    dictionary[Constants.altitude_key] = unpacked_data[1]
    dictionary[Constants.vertical_speed_key] = unpacked_data[2]
    dictionary[Constants.latitude_key] = unpacked_data[3]
    dictionary[Constants.longitude_key] = unpacked_data[4]
    dictionary[Constants.gps_alt_key] = unpacked_data[5]
    dictionary[Constants.fcb_battery_voltage] = unpacked_data[6]
    dictionary[Constants.ground_speed_key] = unpacked_data[7] * 0.514444  # fcb reports speed in kts
    dictionary[Constants.course_over_ground_key] = unpacked_data[8]  # GPS reports compass heading (NED and degrees)
    dictionary[Constants.gps_time_key] = str(datetime.datetime.fromtimestamp(unpacked_data[9]))  # Convert to string so that we aren't passing datetime objects everywhere
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


def parse_cli_message(data: bytes, dictionary):
    """The payload is the string"""
    dictionary[Constants.cli_string_key] = data.decode()


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
                     5: ["CLI Data", parse_cli_message],
                     6: ["Alt Info & Cfg", parse_altitude_info],
                     }
# -1: ["Old transmit stuff", parse_test_message]} #Not used anymore

GROUND_STATION_MESSAGE_TYPES = ["Ground Station GPS"]


def parse_fcb_message(data):
    """Will check packet type, and call the required parse function"""
    dictionary = {}
    message_number = data[0]

    if message_number in MESSAGE_CALLBACKS:
        # Get CRC, LQI, RSSI data from message (First 4)
        radio_data = data[-4:]
        unpacked_radio_status_data = struct.unpack('<BB?B', radio_data)
        # lqi = unpacked_radio_status_data[1] & 0b1111111  # The last 7 bits of the lqi byte are the lqi
        # crc = (unpacked_radio_status_data[1] & 0b10000000)  # And top is CRC

        # Add radio stuff
        radio_id = unpacked_radio_status_data[0]
        rssi = unpacked_radio_status_data[1]
        crc = unpacked_radio_status_data[2]
        lqi = unpacked_radio_status_data[3]

        if rssi != -128:
            rssi_text = "{} db".format(rssi - 50)
        else:
            rssi_text = "Invalid RSSI"

        if radio_id == 0:
            radio_id_string = "433 MHz Radio"
        elif radio_id == 1:
            radio_id_string = "915 MHz Radio"
        else:
            radio_id_string = "Invalid Radio ID"

        crc_str = "Good" if crc else "Bad"

        dictionary[Constants.radio_id_key] = radio_id
        dictionary[Constants.radio_id_string] = radio_id_string
        dictionary[Constants.rssi_key] = rssi_text
        dictionary[Constants.lqi_key] = lqi
        dictionary[Constants.crc_key] = crc_str

        # Get the packet header
        fcb_data = data[0:-4]
        header_data = fcb_data[0:15]
        unpacked_header = struct.unpack('<BBBIBBBBBBBB', header_data)
        dictionary[Constants.software_version_key] = unpacked_header[1]
        dictionary[Constants.serial_number_key] = unpacked_header[2]
        dictionary[Constants.timestamp_ms_key] = unpacked_header[3]

        callsign = ""
        for i in range(4, 11):
            if chr(unpacked_header[i]).isalnum():
                callsign += chr(unpacked_header[i])
        dictionary[Constants.callsign_key] = callsign.strip()

        # Get the rest of the packet
        raw_packet = fcb_data[15:]
        message_type = MESSAGE_CALLBACKS[message_number][0]  # Get message type

        # Parse message
        try:
            MESSAGE_CALLBACKS[message_number][1](raw_packet, dictionary)
            success = True
        except struct.error as e:
            print(e)
            success = False

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
