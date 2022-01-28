"""
Console
"""

from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtWidgets import QLabel, QGridLayout, QWidget

from Widgets import CustomQWidgetBase


class SimpleConsoleWidget(CustomQWidgetBase.CustomQWidgetBase):
    def __init__(self, widget: QWidget = None):
        super().__init__(widget)

        self.data = [[]]

        self.maxLineWidth = 0

        self.setFont(QFont("Monospace", 10))

    def updateConsole(self, data):
        self.data = data

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        """Draw border around widget"""
        painter = QPainter(self)  # Grey background
        painter.setPen(QColor(self.borderColor[0], self.borderColor[1], self.borderColor[2]))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        fontHeight = self.fontInfo().pixelSize()
        for i in range(len(self.data)):
            line = self.data[i]
            if len(line) >= 2:
                color = line[1]
                self.maxLineWidth = max(self.maxLineWidth, len(line[0]))

                if color == 2:
                    painter.setPen(QColor(self.textColor[0], self.textColor[1], self.textColor[2]))
                elif color == 4:
                    painter.setPen(QColor("yellow"))
                elif color == 8 or color == 16:
                    painter.setPen(QColor("red"))
                else:
                    painter.setPen(QColor("blue"))

                painter.drawText(5, fontHeight * (i + 1), line[0])

    def adjustSize(self) -> None:
        height = self.fontInfo().pixelSize() * len(self.data) + 10
        width = int(max(self.fontInfo().pixelSize() * 0.7 * self.maxLineWidth, 1))
        self.resize(width, height)
