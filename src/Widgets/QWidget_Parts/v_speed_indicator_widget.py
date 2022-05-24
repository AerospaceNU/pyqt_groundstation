from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPolygon, QRegion
from PyQt5.QtWidgets import QLabel, QWidget


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


class VSpeedIndicatorWidget(QLabel):
    def __init__(self, parentWidget: QWidget = None, leftOriented=True, maxSpeed=6):
        super().__init__(parentWidget)

        self.size = 200

        self.spacing = 1  # Delta Value between lines
        self.value = 0
        self.maxSpeed = maxSpeed

        self.leftOriented = leftOriented

    def setSize(self, size):
        # TODO: Use the QWidget size functions instead of this sketchy one
        self.size = size

        width = size / 6

        self.setGeometry(0, 0, width, size)
        self.setMinimumWidth(width)
        self.setMaximumWidth(width)
        self.setMinimumHeight(size)
        self.setMaximumHeight(size)

    def paintEvent(self, e):
        painter = QPainter(self)  # Grey background
        painter.setPen(QPen(QColor(50, 50, 50), 0, Qt.SolidLine))
        painter.setBrush(QBrush(QColor(50, 50, 50), Qt.SolidPattern))

        if not self.leftOriented:
            painter.scale(-1, 1)
            painter.translate(-self.width(), 0)

        cornerX = self.width() / 2
        cornerY = self.height() / 8
        cornerHeight = self.height() / 4

        points = [
            QPoint(0, cornerY),
            QPoint(cornerX, cornerY),
            QPoint(self.width(), cornerHeight),
            QPoint(self.width(), self.height() - cornerHeight),
            QPoint(cornerX, self.height() - cornerY),
            QPoint(0, self.height() - cornerY),
        ]
        poly = QPolygon(points)
        painter.drawPolygon(poly)

        maxSpeed = self.maxSpeed
        speedIncrement = self.maxSpeed / 4  # Spacing to draw lines
        numberIncrement = max(self.maxSpeed / 2, 1)  # Spacing to draw numbers
        gaugeHeight = self.height() - 2 * cornerY

        fontSize = max(self.width() / 5, 10)
        padding = fontSize
        painter.setFont(QFont("Monospace", fontSize))

        painter.setPen(QPen(Qt.white, 1, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))

        painter.translate(0, cornerY)
        painter.translate(0, self.height() / 2 - cornerY)

        currentSpeedY = -interpolate(
            clamp(self.value, -maxSpeed, maxSpeed),
            0,
            2 * maxSpeed / speedIncrement,
            0,
            gaugeHeight - padding,
        )

        if abs(self.value) > maxSpeed:
            painter.setPen(QPen(Qt.red, 1, Qt.SolidLine))

        painter.drawLine(
            self.width() * 1.5,
            0,
            self.width() / 3,
            int(currentSpeedY / float(speedIncrement)),
        )

        painter.translate(0, -(self.height() / 2 - cornerY))

        if not self.leftOriented:
            painter.scale(-1, 1)
            painter.translate(-self.width(), 0)

        for i in range(int(maxSpeed / speedIncrement) * 2 + 1):
            y = int(interpolate(i, 0, 2 * maxSpeed / speedIncrement, padding, gaugeHeight - padding))

            if self.leftOriented:
                painter.drawLine(fontSize, y, fontSize + self.width() / 8, y)
            else:
                painter.drawLine(
                    self.width() - fontSize - self.width() / 8,
                    y,
                    self.width() - fontSize,
                    y,
                )

            if (i * speedIncrement) % numberIncrement == 0:
                if self.leftOriented:
                    painter.drawText(
                        0,
                        y + (fontSize / 2),
                        "{}".format(int(abs((i * speedIncrement) - maxSpeed))),
                    )
                else:
                    painter.drawText(
                        self.width() - fontSize,
                        y + (fontSize / 2),
                        "{}".format(int(abs((i * speedIncrement) - maxSpeed))),
                    )

    def setValue(self, value):
        self.value = value
