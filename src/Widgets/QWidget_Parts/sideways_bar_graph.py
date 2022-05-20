from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt5.QtWidgets import QLabel, QWidget

from src.data_helpers import round_to_string


def clamp(value, minValue, maxValue):
    """
    Clamps a value between the min and max value
    """
    return min(max(value, minValue), maxValue)


def interpolate(value, in_min, in_max, out_min, out_max):
    """
    Interpolates a value from the input range to the output range
    """
    in_span = in_max - in_min
    out_span = out_max - out_min

    scaled = float(value - in_min) / float(in_span)
    return out_min + (scaled * out_span)


class SidewaysBarGraph(QLabel):
    def __init__(
        self, parentWidget: QWidget = None, min_value=0, max_value=100, mid_value=None
    ):
        super().__init__(parentWidget)

        self.value = 0
        self.min_value = min_value
        self.max_value = max_value
        self.mid_value = mid_value

        self.setFont(QFont("Monospace", 12))

    def paintEvent(self, e):
        painter = QPainter(self)  # Grey background

        painter.setPen(QPen(QColor(100, 100, 100), 0, Qt.SolidLine))
        painter.setBrush(QBrush(QColor(50, 50, 50), Qt.SolidPattern))

        text = round_to_string(self.value, 4)
        text_width = self.fontInfo().pixelSize() * len(text)
        right_bound = self.width() - text_width
        painter.drawText(
            QRect(right_bound, 0, text_width, self.height()), Qt.AlignCenter, text
        )

        painter.drawRect(0, 0, right_bound - 1, self.height() - 1)

        box_draw_width = interpolate(
            self.value, self.min_value, self.max_value, 1, right_bound - 3
        )
        box_draw_width = int(clamp(box_draw_width, 1, right_bound - 3))

        painter.setBrush(QBrush(QColor(50, 50, 255)))
        painter.setPen(QPen(QColor(50, 50, 255)))

        painter.drawRect(1, 1, box_draw_width, self.height() - 3)

        if self.mid_value is not None:
            painter.setPen(QPen(QColor(100, 100, 100), 0, Qt.SolidLine))
            mid_line_draw_location = interpolate(
                self.mid_value, self.min_value, self.max_value, 1, right_bound - 3
            )
            painter.drawLine(
                mid_line_draw_location, 0, mid_line_draw_location, self.height()
            )

    def setValue(self, value):
        self.value = value

    def setMidValue(self, mid_value):
        self.mid_value = mid_value
