from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PyQt5.QtCore import Qt, QRect


def clamp(value, min_value, max_value):
    """
    Clamps a value between the min and max value
    """
    return min(max(value, min_value), max_value)


def interpolate(value, in_min, in_max, out_min, out_max):
    """
    Interpolates a value from the input range to the output range
    """
    in_span = in_max - in_min
    out_span = out_max - out_min

    scaled = float(value - in_min) / float(in_span)
    return out_min + (scaled * out_span)


class CircleBarGraphWidget(QLabel):
    def __init__(self, parent_widget: QWidget = None, title="Title", min_value=0, max_value=100, size=200, bar_color=None):
        super().__init__(parent_widget)
        self.size = size
        self.value = 0
        self.title = title

        self.minValue = min_value
        self.maxValue = max_value

        if bar_color is not None:
            [red, green, blue] = [int(float(i)) for i in bar_color.split("(")[1].split(")")[0].split(",")]
            self.barColor = QColor(red, green, blue)
        else:
            self.barColor = QColor(50, 50, 255)

        self.textColor = QColor(255, 255, 255)

        self.setAlignment(Qt.AlignCenter)

    def setSize(self, size):
        # TODO: Use the QWidget size functions instead of this sketchy one
        self.size = size

        self.setGeometry(0, 0, size, size)
        self.setMinimumWidth(size)
        self.setMaximumWidth(size)
        self.setMinimumHeight(size)
        self.setMaximumHeight(size)

    def paintEvent(self, e):
        painter = QPainter(self)  # Grey background

        font_size = max(int(self.width() * 0.1), 8)
        padding = 4
        painter.setPen(QPen(self.textColor, 1, Qt.SolidLine))
        painter.setFont(QFont("Monospace", font_size))
        font_height = int(font_size * 1.5)

        value_text = str(self.value)[0:6]
        painter.drawText(QRect(0, 0, self.width(), self.height() * 0.9), Qt.AlignCenter, value_text)

        small_font_size = max(font_size / 2, 6)
        painter.setFont(QFont("Monospace", small_font_size))
        painter.drawText(QRect(0, (self.height() * 0.9 / 2) + small_font_size + padding, self.width(), small_font_size), Qt.AlignCenter, self.title)

        theta = clamp(interpolate(self.value, self.minValue, self.maxValue, 0, 360 * 16), 0, 360 * 16)
        bar_padding = 5

        line_width = int(self.size / 7)
        painter.setPen(QPen(self.barColor, line_width, Qt.SolidLine))
        painter.translate(0, self.height())
        painter.rotate(-90)

        painter.drawArc(bar_padding, bar_padding, self.width() - 2 * bar_padding, self.height() - 2 * bar_padding, 0, -theta)

    def setValue(self, value):
        self.value = value

    def setTextColor(self, text_color: str):
        if "rgb" in text_color:
            [red, green, blue] = [int(float(i)) for i in text_color.split("(")[1].split(")")[0].split(",")]
            self.textColor = QColor(red, green, blue)
        else:
            self.textColor = QColor(text_color)

    @staticmethod
    def getType():
        return "CircleBarGraph"

    def getLimits(self):
        return [self.minValue, self.maxValue]

    def getMin(self):
        return str(self.minValue)

    def getMax(self):
        return str(self.maxValue)

    def getColor(self):
        color_string = "rgb({0},{1},{2})".format(self.barColor.red(), self.barColor.green(), self.barColor.blue())
        return color_string
