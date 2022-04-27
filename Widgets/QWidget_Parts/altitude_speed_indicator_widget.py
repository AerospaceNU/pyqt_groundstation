from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtGui import QPainter, QPen, QBrush, QPolygon, QColor, QFont
from PyQt5.QtCore import Qt, QPoint

from data_helpers import round_to_string, nearest_multiple, clamp


class AltitudeSpeedIndicatorWidget(QLabel):
    def __init__(self, parent_widget: QWidget = None, left_oriented=True, text_spacing=1, pixels_per_line=10, intermediate_lines=1):
        super().__init__(parent_widget)

        self.size = 200

        self.textSpacing = text_spacing  # Delta Value between lines
        self.intermediateLines = int(intermediate_lines)  # Number of lines to draw between text
        self.pixelsPerLine = int(pixels_per_line)
        self.deltaValuePerTick = 0.4 * float(self.textSpacing)

        self.value = 0
        self.commandedValue = 0

        self.leftOriented = left_oriented

    def setSize(self, size):
        # TODO: Use the QWidget size functions instead of this sketchy one
        self.size = size

        self.setGeometry(0, 0, size / 4, size)
        self.setMinimumWidth(size / 4)
        self.setMaximumWidth(size / 4)
        self.setMinimumHeight(size)
        self.setMaximumHeight(size)

    def paintEvent(self, e):
        short_length = 10
        font_size = max(self.width() / 5, 10)

        # Limit the rate at which the value can change, so that the output looks like its moving
        if self.commandedValue > self.value:
            self.value = min(self.value + self.deltaValuePerTick, self.commandedValue)
        elif self.commandedValue < self.value:
            self.value = max(self.value - self.deltaValuePerTick, self.commandedValue)

        painter = QPainter(self)  # Grey background
        painter.setPen(QPen(QColor(50, 50, 50), 0, Qt.SolidLine))
        painter.setBrush(QBrush(QColor(50, 50, 50), Qt.SolidPattern))
        painter.drawRect(0, 0, self.width(), self.height())
        painter.setFont(QFont("Monospace", font_size))

        line_width = self.height() / 100

        painter.translate(int(self.width() / 2), int(self.height() / 2))  # Set our coordinate system to be centered on the widget
        painter.setPen(QPen(Qt.white, line_width, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))

        lines_to_draw = (self.height() / 2) / (self.pixelsPerLine / (self.intermediateLines + 1))
        line_delta_value = self.textSpacing / (self.intermediateLines + 1)

        start_x = int(self.width() / 2)
        end_x = int(self.width() / 2) - short_length

        if self.leftOriented:
            start_x = -start_x
            end_x = -end_x

        rounded_value = nearest_multiple(self.value, self.textSpacing)
        delta_value_per_pixel = float(self.textSpacing) / float(self.pixelsPerLine)
        center_offset_pixels = float(rounded_value - self.value) / float(delta_value_per_pixel)
        line_pixel_spacing = self.pixelsPerLine / (self.intermediateLines + 1)

        for i in range(-int(lines_to_draw), int(lines_to_draw + 2)):
            line_y_position = (i * line_pixel_spacing) - center_offset_pixels
            painter.drawLine(start_x, line_y_position, end_x, line_y_position)

            if i % (self.intermediateLines + 1) == 0:
                value = round_to_string(rounded_value + (-i * line_delta_value), 4)
                if self.leftOriented:
                    painter.drawText(end_x + 5, line_y_position + int(font_size / 2), "{}".format(value))
                else:
                    painter.drawText(end_x - 5 - (4 * (font_size - 2)), line_y_position + int(font_size / 2), "{:>3}".format(value))

        pointer_corner_x = int(self.width() / 5)
        pointer_height = int(self.height() / 20)

        painter.setPen(QPen(Qt.white, 2, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))

        if self.leftOriented:
            points = [
                QPoint(-pointer_corner_x, pointer_height),
                QPoint(self.width() / 2, pointer_height),
                QPoint(self.width() / 2, -pointer_height),
                QPoint(-pointer_corner_x, -pointer_height),
                QPoint(-self.width() / 2, 0),
            ]
        else:
            points = [
                QPoint(pointer_corner_x, pointer_height),
                QPoint(-self.width() / 2, pointer_height),
                QPoint(-self.width() / 2, -pointer_height),
                QPoint(pointer_corner_x, -pointer_height),
                QPoint(self.width() / 2, 0),
            ]
        poly = QPolygon(points)
        painter.drawPolygon(poly)

        font_size = int(font_size * 0.8)
        painter.setFont(QFont("Monospace", font_size))
        if self.leftOriented:
            painter.drawText(int(-2 * (font_size - 2)), int(font_size / 2), round_to_string(self.value, 5))
        else:
            painter.drawText(int(-3 * (font_size - 2)), int(font_size / 2), round_to_string(self.value, 5))

    def setValue(self, value):
        self.commandedValue = value
