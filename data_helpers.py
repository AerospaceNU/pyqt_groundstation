import math
from PyQt5.QtGui import QColor

"""
Some functions to help with repetitive tasks
"""


def clamp(value, minValue, maxValue):
    """
    Clamps a value between the min and max value
    """
    return min(max(value, minValue), maxValue)


def vector_length(x, y):
    return math.sqrt(x ** 2 + y ** 2)


def distance_between_points(x, y, x2, y2):
    deltaX = x2 - x
    deltaY = y2 - y

    return vector_length(deltaX, deltaY)


def interpolate(value, in_min, in_max, out_min, out_max):
    """
    Interpolates a value from the input range to the output range
    """
    in_span = in_max - in_min
    out_span = out_max - out_min

    scaled = float(value - in_min) / float(in_span)
    return out_min + (scaled * out_span)


def nearest_multiple(value, base):
    return base * round(value / base)


def get_value_from_dictionary(dictionary: {}, key: str, default):
    """
    Returns the dictionary entry for a given key, or the default
    """

    if key in dictionary:
        if type(dictionary[key]) == float and math.isnan(dictionary[key]):
            return default
        else:
            return dictionary[key]
    else:
        return default


def get_value_from_list(inputList: list, index: int, default):
    if len(inputList) > index:
        return inputList[index]
    else:
        return default


def check_type(value, data_type):
    if type(value) == data_type:
        return True

    try:
        data_type(value)
        return True
    except:
        return False


def get_rgb_from_string(textColor: str):
    """
    Function to get red, green, and blue as integer values from 0-255
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
    return "rgb({0}, {1}, {2})".format(red, green, blue)


def get_well_formatted_rgb_string(inputString):
    """
    Function that returns a string like "rgb(red,green,blue)" for use with QT stylesheets from a variety of input types
    """
    [red, green, blue] = get_rgb_from_string(inputString)
    return format_rgb_string(red, green, blue)


def get_qcolor_from_string(input_string):
    [red, green, blue] = get_rgb_from_string(input_string)
    return QColor.fromRgb(red, green, blue)


def make_stylesheet_string(target, rgbString):
    return "{0}: {1}; ".format(target, rgbString)


def first_in_list_larger_than(data_list: list, threshold):
    if len(data_list) != 0:
        for element in data_list:
            if element > threshold:
                return element

    return None


def first_index_in_list_larger_than(data_list: list, threshold):
    value = first_in_list_larger_than(data_list, threshold)

    if value is not None:
        return data_list.index(value)
    else:
        return None


def round_to_string(value: float, characters: int):
    """
    Creates a nicely formatted string of a specific length from a number
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
