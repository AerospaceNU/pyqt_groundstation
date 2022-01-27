import math

"""
Some functions to help with repetitive tasks
"""


def clamp(value, minValue, maxValue):
    """
    Clamps a value between the min and max value
    """
    return min(max(value, minValue), maxValue)


def distanceBetweenPoints(x, y, x2, y2):
    deltaX = x2 - x
    deltaY = y2 - y

    return math.sqrt(deltaX ** 2 + deltaY ** 2)


def interpolate(value, in_min, in_max, out_min, out_max):
    """
    Interpolates a value from the input range to the output range
    """
    in_span = in_max - in_min
    out_span = out_max - out_min

    scaled = float(value - in_min) / float(in_span)
    return out_min + (scaled * out_span)


def getXMLAttribute(XLM, attribute: str, default: str):
    """
    Returns the value from a chunk of xml data, with the option for a default value
    :param XLM: the chunk of xml data
    :param attribute: the name of the attribute to get
    :param default: default value
    """
    if XLM.hasAttribute(attribute):
        return XLM.getAttribute(attribute)
    else:
        return default


def getValueFromDictionary(dictionary: {}, key: str, default):
    """
    Returns the dictionary entry for a given key, or the default
    """

    if key in dictionary:
        return dictionary[key]
    else:
        return default


def getValueFromList(inputList: list, index: int, default):
    if len(inputList) > index:
        return inputList[index]
    else:
        return default


def getRGBFromString(textColor: str):
    """
    Function to get red, green, and blue as integer values from 0-255
    """
    if "rgb[" in textColor:
        [red, green, blue] = textColor.split("[")[1].split("]")[0].split(",")
    elif "rgb(" in textColor:
        [red, green, blue] = textColor.split("(")[1].split(")")[0].split(",")
    else:
        print("Invalid color string: {}".format(textColor))
        [red, green, blue] = [0, 0, 0]

    return [int(red), int(green), int(blue)]


def formatRGBString(red, green, blue):
    return "rgb({0}, {1}, {2})".format(red, green, blue)


def getWellFormattedRGBString(inputString):
    """
    Function that returns a string like "rgb(red,green,blue)" for use with QT stylesheets from a variety of input types
    """
    [red, green, blue] = getRGBFromString(inputString)
    return formatRGBString(red, green, blue)


def makeStylesheetString(target, rgbString):
    return "{0}: {1}; ".format(target, rgbString)


def roundToString(value: float, characters: int):
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
        while len(string) < characters:
            string += "0"

    return string
