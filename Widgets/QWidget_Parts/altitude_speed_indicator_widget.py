from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtGui import QPainter, QPen, QBrush, QPolygon, QColor, QFont, QRegion
from PyQt5.QtCore import Qt, QPoint

from data_helpers import round_to_string


class AltitudeSpeedIndicatorWidget(QLabel):
    def __init__(self, parentWidget: QWidget = None, leftOriented=True, lineSpacing=1, textSpacing=1):
        super().__init__(parentWidget)

        self.size = 200

        self.textSpacing = textSpacing  # Delta Value between lines
        self.lineSpacing = lineSpacing  # Delta Value between text
        self.value = 0

        self.leftOriented = leftOriented

    def setSize(self, size):
        # TODO: Use the QWidget size functions instead of this sketchy one
        self.size = size

        self.setGeometry(0, 0, size / 4, size)
        self.setMinimumWidth(size / 4)
        self.setMaximumWidth(size / 4)
        self.setMinimumHeight(size)
        self.setMaximumHeight(size)

    def paintEvent(self, e):
        pixelsPerLine = 10
        shortLength = 10
        fontSize = max(self.width() / 5, 10)

        painter = QPainter(self)  # Grey background
        painter.setPen(QPen(QColor(50, 50, 50), 0, Qt.SolidLine))
        painter.setBrush(QBrush(QColor(50, 50, 50), Qt.SolidPattern))
        painter.drawRect(0, 0, self.width(), self.height())
        painter.setFont(QFont("Monospace", fontSize))

        lineWidth = self.height() / 100

        painter.translate(int(self.width() / 2), int(self.height() / 2))  # Set our coordinate system to be centered on the widget
        painter.setPen(QPen(Qt.white, lineWidth, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))

        linesToDraw = (self.height() / 2) / pixelsPerLine

        startX = int(self.width() / 2)
        endX = int(self.width() / 2) - shortLength

        if self.leftOriented:
            startX = -startX
            endX = -endX

        for i in range(-int(linesToDraw), int(linesToDraw+2), self.lineSpacing):
            lineYPosition = i * pixelsPerLine
            painter.drawLine(startX, lineYPosition, endX, lineYPosition)

            if i % 2 == 0:
                value = round_to_string(-(self.value + (float(i) * float(pixelsPerLine) * self.textSpacing)), 4)
                if self.leftOriented:
                    painter.drawText(endX + 5, lineYPosition + int(fontSize / 2), "{}".format(value))
                else:
                    painter.drawText(endX - 5 - (4 * (fontSize - 2)), lineYPosition + int(fontSize / 2), "{:>3}".format(value))

        pointerCornerX = int(self.width() / 5)
        pointerHeight = int(self.height() / 20)

        painter.setPen(QPen(Qt.white, 2, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))

        if self.leftOriented:
            points = [
                QPoint(-pointerCornerX, pointerHeight),
                QPoint(self.width() / 2, pointerHeight),
                QPoint(self.width() / 2, -pointerHeight),
                QPoint(-pointerCornerX, -pointerHeight),
                QPoint(-self.width() / 2, 0),
            ]
        else:
            points = [
                QPoint(pointerCornerX, pointerHeight),
                QPoint(-self.width() / 2, pointerHeight),
                QPoint(-self.width() / 2, -pointerHeight),
                QPoint(pointerCornerX, -pointerHeight),
                QPoint(self.width() / 2, 0),
            ]
        poly = QPolygon(points)
        painter.drawPolygon(poly)

        fontSize = int(fontSize * 0.8)
        painter.setFont(QFont("Monospace", fontSize))
        if self.leftOriented:
            painter.drawText(int(-2 * (fontSize - 2)), int(fontSize / 2), round_to_string(self.value, 5))
        else:
            painter.drawText(int(-3 * (fontSize - 2)), int(fontSize / 2), round_to_string(self.value, 5))

    def setValue(self, value):
        self.value = value
