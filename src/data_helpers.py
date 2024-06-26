"""
Some functions to help with repetitive tasks
"""

import math
from dataclasses import dataclass

import numpy
from PyQt5.QtGui import QColor


@dataclass
class InfoColorPalette(object):
    info_color: QColor
    warn_color: QColor
    error_color: QColor


def clamp(value, minValue, maxValue):
    """Clamps a value between the min and max value"""
    return min(max(value, minValue), maxValue)


def vector_length(x, y):
    """Returns length of vector [x, y]"""
    return math.sqrt(x**2 + y**2)


def quaternion_to_euler_angle(quaternion):
    """quaternion in xyzw to euler angles in radians"""
    [w, x, y, z] = quaternion

    ysqr = y * y

    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + ysqr)
    X = numpy.arctan2(t0, t1)

    t2 = +2.0 * (w * y - z * x)
    t2 = numpy.where(t2 > +1.0, +1.0, t2)
    # t2 = +1.0 if t2 > +1.0 else t2

    t2 = numpy.where(t2 < -1.0, -1.0, t2)
    # t2 = -1.0 if t2 < -1.0 else t2
    Y = numpy.arcsin(t2)

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (ysqr + z * z)
    Z = numpy.arctan2(t3, t4)

    return [X, Y, Z]


def euler_to_quaternion(roll, pitch, yaw):
    qx = numpy.sin(roll / 2) * numpy.cos(pitch / 2) * numpy.cos(yaw / 2) - numpy.cos(roll / 2) * numpy.sin(pitch / 2) * numpy.sin(yaw / 2)
    qy = numpy.cos(roll / 2) * numpy.sin(pitch / 2) * numpy.cos(yaw / 2) + numpy.sin(roll / 2) * numpy.cos(pitch / 2) * numpy.sin(yaw / 2)
    qz = numpy.cos(roll / 2) * numpy.cos(pitch / 2) * numpy.sin(yaw / 2) - numpy.sin(roll / 2) * numpy.sin(pitch / 2) * numpy.cos(yaw / 2)
    qw = numpy.cos(roll / 2) * numpy.cos(pitch / 2) * numpy.cos(yaw / 2) + numpy.sin(roll / 2) * numpy.sin(pitch / 2) * numpy.sin(yaw / 2)

    return [qx, qy, qz, qw]


def distance_between_points(x, y, x2, y2):
    """Returns distance between [x, y] and [x2, y2]"""
    deltaX = x2 - x
    deltaY = y2 - y

    return vector_length(deltaX, deltaY)


def interpolate(value, in_min, in_max, out_min, out_max):
    """Interpolates a value from the input range to the output range"""

    in_span = in_max - in_min
    out_span = out_max - out_min

    scaled = float(value - in_min) / float(in_span)
    return out_min + (scaled * out_span)


def nearest_multiple(value, base):
    """Returns the nearest multiple of [base] to [value]"""

    return base * round(value / base)


def get_value_from_dictionary(dictionary: {}, key: str, default):
    """Returns the dictionary entry for a given key, or the default if that value doesn't exist"""

    if key in dictionary:
        if type(dictionary[key]) == float and math.isnan(dictionary[key]):
            return default
        else:
            return dictionary[key]
    else:
        return default


def get_value_from_list(inputList: list, index: int, default):
    """Returns the value in the list at the index specified, or the default if that index doesn't exist"""

    if len(inputList) > index:
        return inputList[index]
    else:
        return default


def check_type(value, data_type):
    """
    Returns true if value is or can be converted to data_type

    for example: check_type(3.0, float) would return true, and check_type("3.0", float) would also return true
    """

    if type(value) == data_type:
        return True

    try:
        data_type(value)
        return True
    except Exception:
        return False


def get_rgb_from_qcolor(q_color: QColor):
    return [q_color.red(), q_color.green(), q_color.blue()]


def get_rgb_from_string(textColor: str):
    """
    Function to get red, green, and blue as integer values from 0-255

    returns [red, green, blue]
    """

    if "rgb[" in textColor:
        [red, green, blue] = textColor.split("[")[1].split("]")[0].split(",")
    elif "rgb(" in textColor:
        [red, green, blue] = textColor.split("(")[1].split(")")[0].split(",")
    else:
        # print("Invalid color string: {}".format(textColor))
        [red, green, blue] = [0, 0, 0]

    return [int(red), int(green), int(blue)]


def format_rgb_string(red, green, blue):
    """Makes Qt style rgb(red,green,blue) formatted string from the individual values"""

    return "rgb({0}, {1}, {2})".format(red, green, blue)


def get_well_formatted_rgb_string(input_val):
    """Function that returns a string like "rgb(red,green,blue)" for use with QT stylesheets from a variety of input string types"""

    if type(input_val) == str:
        [red, green, blue] = get_rgb_from_string(input_val)
    elif type(input_val) == QColor:
        [red, green, blue] = get_rgb_from_qcolor(input_val)
    else:
        return

    return format_rgb_string(red, green, blue)


def get_qcolor_from_string(input_string):
    """Returns a QColor object from the input string"""
    [red, green, blue] = get_rgb_from_string(input_string)
    return QColor.fromRgb(red, green, blue)


def get_text_from_qcolor(q_color: QColor):
    """Make Qt style string from a QColor object"""
    return format_rgb_string(q_color.red(), q_color.green(), q_color.blue())


def make_stylesheet_string(target, rgbString):
    """Returns PyQt stylesheet formatted string: [target: rgbString;]"""
    return "{0}: {1}; ".format(target, rgbString)


def generateDarkerColor(input_color, delta):
    """returns a PyQt formatted rgb string that is darker than the input color string"""
    r_g_b = get_rgb_from_string(input_color)
    r_g_b[0] = clamp(r_g_b[0] - delta, 0, 255)
    r_g_b[1] = clamp(r_g_b[1] - delta, 0, 255)
    r_g_b[2] = clamp(r_g_b[2] - delta, 0, 255)
    return format_rgb_string(r_g_b[0], r_g_b[1], r_g_b[2])


def first_in_list_larger_than(data_list: list, threshold):
    """Looks through list until it finds a value larger than threshold, and returns that.  If none are found, it returns None"""
    if len(data_list) != 0:
        for element in data_list:
            if element > threshold:
                return element

    return None


def first_index_in_list_larger_than(data_list: list, threshold):
    """Returns index of first value larger than threshold.  if None are found, returns none"""

    value = first_in_list_larger_than(data_list, threshold)

    if value is not None:
        return data_list.index(value)
    else:
        return None


def round_to_string(value: float, characters: int):
    """
    Creates a nicely formatted string of a specific length from a number
    Obviously this can't always return a string that is the correct length for example round_to_string(10000, 2) will return "10000"
    But it does a pretty good job most of the time
    """

    if value == 0:
        return " " * (characters - 1) + "0"  # Sometimes python is cool

    if abs(value) < 1:
        leadingZeros = math.ceil(abs(math.log10(abs(value)))) - 1
        if leadingZeros >= characters - 1:
            string = " " * (characters - 1) + "0"
        else:
            if value < 0:
                padding = 3  # Represents the number of "extra" characters (eg periods, negative signs, or leading 0s)
            else:
                padding = 2
            string = "{}".format(round(value, characters - padding))
    else:
        preDecimalLength = math.floor(math.log10(abs(value))) + 1
        if value < 0:
            preDecimalLength += 1

        string = "{}".format(round(value, characters - preDecimalLength - 1))

        if "." in string and len(string) > characters:
            string = string.split(".")[0]

        while len(string) < characters:
            string = " " + string

    return string


def get_info_color_palette_from_background(background_color: QColor) -> InfoColorPalette:
    rgb = get_rgb_from_qcolor(background_color)

    if sum(rgb) > 255:  # Can't see the yellow with a bright background
        return InfoColorPalette(
            info_color=QColor(0, 150, 0),
            warn_color=QColor(255, 150, 0),
            error_color=QColor(255, 50, 50),
        )
    else:
        return InfoColorPalette(
            info_color=QColor(0, 150, 0),
            warn_color=QColor(255, 255, 0),
            error_color=QColor(255, 0, 0),
        )


def get_warn_color_from_background(background_color: QColor) -> QColor:
    return get_info_color_palette_from_background(background_color).warn_color
