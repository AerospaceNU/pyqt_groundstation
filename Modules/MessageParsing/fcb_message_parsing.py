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

    if min == float('nan'):
        print("Found a NaN while parsing lat/lon data")
        return 0

    abs_val = abs(min)
    sign = numpy.sign(min)
    return (math.trunc(float(abs_val) / 100.0) + (float(abs_val) % 100.0) / 60.0) * sign


def parse_pyro_continuity_byte(pyro_cont):
    pyro_list = []
    for i in range(Constants.MAX_PYROS):
        has_cont_b = (pyro_cont & (1 << i)) > 0
        pyro_list.append(has_cont_b)

    return pyro_list


def parse_pyro_fire_status(pyro_status):
    pyro_list = []
    for i in range(8):
        pyro_list.append(bool((pyro_status >> i) & 1))

    return pyro_list


def get_fcb_state_from_state_num(state_num):
    if state_num < len(Constants.fcb_state_names):
        return Constants.fcb_state_names[state_num]
    else:
        return Constants.invalid_fcb_state_name


UINT_8_TYPE = 'B'
INT_8_TYPE = 'b'
BOOL_TYPE = '?'

UINT_16_TYPE = 'H'
UINT_32_TYPE = 'I'

FLOAT_TYPE = 'f'


class BaseMessage(object):
    messageData = []

    def __init__(self):
        """
        Base class for a message.
        Contains all the generic logic needed to parse one into a dictionary
        """

        self.byteOrder = "<"  # Make the string to pass to the struct library
        for data_point in self.messageData:
            self.byteOrder += data_point[0]

    def parseMessage(self, data):
        """
        Returns a dictionary of values from the binary data in the message
        """

        dictionary = {}

        message_length = struct.calcsize(self.byteOrder)
        data = data[0:message_length]
        unpacked_data = struct.unpack(self.byteOrder, data)

        if len(unpacked_data) != len(self.messageData):
            print("length mismatch")

        for i in range(len(self.messageData)):
            message_line = self.messageData[i]

            if len(message_line) == 2:
                dictionary[message_line[1]] = unpacked_data[i]
            else:
                parse_type = message_line[2]
                key = message_line[1]

                # Various special options to parse
                if type(parse_type) == int or type(parse_type) == float:  # If it's a number, just multiply
                    dictionary[key] = unpacked_data[i] * parse_type
                elif parse_type == "TIME":  # If its a time, make a time string
                    dictionary[key] = str(datetime.datetime.fromtimestamp(unpacked_data[i]))
                elif callable(parse_type):  # If its a function
                    dictionary[key] = parse_type(unpacked_data[i])
                else:
                    print("Unknown parse type")

        self.extraParseOptions(data, dictionary)

        return dictionary

    def extraParseOptions(self, data, dictionary):
        """
        Override this to add more functionality
        """

        pass


class OrientationMessage(BaseMessage):
    """uint8 state, int8 qw, qx, qy, qz, float wx, wy, wz, ax, ay, az, bx, by, bz;"""

    messageData = [[UINT_8_TYPE, Constants.fcb_state_number_key],
                   [INT_8_TYPE, "qw", 0.001],
                   [INT_8_TYPE, "qx", 0.001],
                   [INT_8_TYPE, "qy", 0.001],
                   [INT_8_TYPE, "qz", 0.001],
                   [FLOAT_TYPE, Constants.rotational_velocity_x_key],
                   [FLOAT_TYPE, Constants.rotational_velocity_y_key],
                   [FLOAT_TYPE, Constants.rotational_velocity_z_key],
                   [FLOAT_TYPE, Constants.acceleration_x_key],
                   [FLOAT_TYPE, Constants.acceleration_y_key],
                   [FLOAT_TYPE, Constants.acceleration_z_key],
                   [FLOAT_TYPE, Constants.magnetometer_x_key],
                   [FLOAT_TYPE, Constants.magnetometer_y_key],
                   [FLOAT_TYPE, Constants.magnetometer_z_key],
                   ]

    def __init__(self):
        super().__init__()

    def extraParseOptions(self, data, dictionary):
        qx = dictionary.pop('qx')
        qy = dictionary.pop("qy")
        qz = dictionary.pop("qz")
        qw = dictionary.pop("qw")

        rpy = quaternion_to_euler_angle(qw, qx, qy, qz)

        dictionary[Constants.roll_position_key] = rpy[0]
        dictionary[Constants.pitch_position_key] = rpy[1]
        dictionary[Constants.yaw_position_key] = rpy[2]

        dictionary[Constants.orientation_quaternion_key] = [qw, qx, qy, qz]
        dictionary[Constants.orientation_rpy_key] = rpy

        # I don't use these
        # dictionary[Constants.rotational_velocity_key] = [wx, wy, wz]
        # dictionary[Constants.acceleration_vector_key] = [ax, ay, az]
        # dictionary[Constants.magnetic_vector_key] = [bx, by, bz]


class PositionDataMessage(BaseMessage):
    messageData = [[FLOAT_TYPE, Constants.temperature_key],
                   [FLOAT_TYPE, Constants.altitude_key],
                   [FLOAT_TYPE, Constants.vertical_speed_key],
                   [FLOAT_TYPE, Constants.latitude_key, lat_lon_decimal_minutes_to_decimal_degrees],
                   [FLOAT_TYPE, Constants.longitude_key, lat_lon_decimal_minutes_to_decimal_degrees],
                   [FLOAT_TYPE, Constants.gps_alt_key],
                   [FLOAT_TYPE, Constants.fcb_battery_voltage],
                   [FLOAT_TYPE, Constants.ground_speed_key, 0.514444],  # fcb reports speed in kts
                   [FLOAT_TYPE, Constants.course_over_ground_key],  # GPS reports compass heading (NED and degrees)
                   [UINT_32_TYPE, Constants.gps_time_key, "TIME"],
                   [UINT_8_TYPE, Constants.gps_sats_key],
                   [UINT_8_TYPE, Constants.pyro_continuity, parse_pyro_continuity_byte],
                   [UINT_8_TYPE, Constants.fcb_state_number_key],
                   [UINT_8_TYPE, Constants.bluetooth_connection_key],
                   ]


class LineCutterMessage(BaseMessage):
    """uint8 number state uint32 timestamp float avgAlt avgDeltaAlt uint8 batt bool cut_1 cut_2 uint16 photoresistor"""

    def parseMessage(self, data):
        """We generate the message format after parsing which line cutter this data is for."""

        # data = data[0:1]
        unpacked_data = struct.unpack("<B", data[0:1])  # Just get the first byte
        line_cutter_number = unpacked_data[0]

        self.messageData = [[UINT_8_TYPE, Constants.line_cutter_number_key],
                            [UINT_8_TYPE, Constants.makeLineCutterString(line_cutter_number, Constants.line_cutter_state_key)],
                            [UINT_32_TYPE, Constants.makeLineCutterString(line_cutter_number, Constants.timestamp_ms_key)],
                            [UINT_32_TYPE, Constants.makeLineCutterString(line_cutter_number, Constants.barometer_pressure_key)],
                            [FLOAT_TYPE, Constants.makeLineCutterString(line_cutter_number, Constants.altitude_key)],
                            [FLOAT_TYPE, Constants.makeLineCutterString(line_cutter_number, Constants.delta_altitude_key)],
                            [FLOAT_TYPE, Constants.makeLineCutterString(line_cutter_number, Constants.temperature_key)],
                            [FLOAT_TYPE, Constants.makeLineCutterString(line_cutter_number, Constants.acceleration_key)],
                            [FLOAT_TYPE, Constants.makeLineCutterString(line_cutter_number, Constants.battery_voltage_key)],
                            [UINT_16_TYPE, Constants.makeLineCutterString(line_cutter_number, Constants.line_cutter_cut_1)],
                            [UINT_16_TYPE, Constants.makeLineCutterString(line_cutter_number, Constants.line_cutter_cut_2)],
                            [UINT_16_TYPE, Constants.makeLineCutterString(line_cutter_number, Constants.line_cutter_current_sense_key)],
                            [UINT_16_TYPE, Constants.makeLineCutterString(line_cutter_number, Constants.photoresistor_key)],
                            ]

        super().__init__()

        return super().parseMessage(data)  # Then call the parent parseMessage function like normal


class CLIDataMessage(BaseMessage):
    """The payload is the string"""

    def parseMessage(self, data):
        length = data[0]
        trimmed_data = data[1:length + 1]
        dictionary = {}

        try:
            string = trimmed_data.decode()
            dictionary[Constants.cli_string_key] = string
        except Exception as e:
            print(e)

        return dictionary


class AltitudeInfoMessage(BaseMessage):
    messageData = [[FLOAT_TYPE, Constants.barometer_pressure_key],
                   [FLOAT_TYPE, Constants.barometer_pressure_2_key],
                   [FLOAT_TYPE, Constants.press_ref_key],
                   [FLOAT_TYPE, Constants.ground_elevation_key],
                   [FLOAT_TYPE, Constants.ground_temp_key],
                   ]


class PyroInfoMessage(BaseMessage):
    messageData = [[UINT_8_TYPE, Constants.pyro_continuity, parse_pyro_continuity_byte],
                   [UINT_8_TYPE, Constants.pyro_fire_status, parse_pyro_fire_status],
                   ]


# Dictionary {[message_number]: [[name], [callback]]}
MESSAGE_CALLBACKS = {2: ["Orientation", OrientationMessage],
                     3: ["Position Data", PositionDataMessage],
                     4: ["Line Cutter ", LineCutterMessage],
                     5: ["CLI Data", CLIDataMessage],
                     6: ["Alt Info & Cfg", AltitudeInfoMessage],
                     7: ["Pyro Info", PyroInfoMessage]
                     }


# Ground station messages
def parse_ground_station_gps(data, dictionary):
    unpacked_data = struct.unpack("<Bfffdd", data)
    dictionary[Constants.ground_station_latitude_key] = lat_lon_decimal_minutes_to_decimal_degrees(unpacked_data[1])
    dictionary[Constants.ground_station_longitude_key] = lat_lon_decimal_minutes_to_decimal_degrees(unpacked_data[2])
    dictionary[Constants.ground_station_altitude_key] = unpacked_data[3]
    dictionary[Constants.ground_station_pressure_key] = unpacked_data[4]
    dictionary[Constants.ground_station_temperature_key] = unpacked_data[5]


GROUND_STATION_MESSAGE_TYPES = ["Ground Station GPS"]


def parse_fcb_message(data):
    """Will check packet type, and call the required parse function"""
    dictionary = {}
    message_number = data[0]

    if message_number in MESSAGE_CALLBACKS:
        # Get CRC, LQI, RSSI data from message (First 4)
        radio_data = data[-4:]
        unpacked_radio_status_data = struct.unpack('<Bb?B', radio_data)
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
            message_object = MESSAGE_CALLBACKS[message_number][1]()  # Make instance of message class
            dictionary.update(message_object.parseMessage(raw_packet))  # Run the parse method
            success = True

            if "line cutter" in message_type.lower() and Constants.line_cutter_number_key in dictionary:
                line_cutter_number = dictionary[Constants.line_cutter_number_key]
                message_type += str(line_cutter_number)
        except Exception as e:
            print("Could not parse message of type {0}: {1}".format(message_type, e))
            print(raw_packet)
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
