"""
Console
"""

import logging

from PyQt5 import QtGui
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QWidget

from src.Widgets import custom_q_widget_base


class SimpleConsoleWidget(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.data = [[]]

        self.maxLineWidth = 0

    def updateConsole(self, data):
        self.data = data

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        """Draw border around widget"""
        painter = QPainter(self)  # Grey background

        self.maxLineWidth = 0
        font_height = self.fontInfo().pixelSize()
        for i in range(len(self.data)):
            line = self.data[i]
            if len(line) >= 2:
                color = line[1]
                text = str(line[0].strip())

                self.maxLineWidth = max(self.maxLineWidth, len(text))

                if color == logging.INFO or color == logging.DEBUG:
                    painter.setPen(self.palette().text().color())
                elif color == logging.WARNING:
                    painter.setPen(self.getInfoColorPalette().warn_color)
                elif color == logging.ERROR:
                    painter.setPen(self.getInfoColorPalette().error_color)
                else:
                    painter.setPen(QColor("blue"))

                painter.drawText(5, font_height * (i + 1), text)

    def adjustSize(self) -> None:
        height = self.fontInfo().pixelSize() * len(self.data) + 10
        width = int(max(self.fontInfo().pixelSize() * 0.65 * self.maxLineWidth, 1))
        self.resize(width, height)

    def addCustomMenuItems(self, menu, e):
        menu.addAction("Clear console", self.clearConsole)

    def clearConsole(self):
        self.requestCallback("clear_console", "")

    def customUpdateAfterThemeSet(self):
        self.setStyleSheet("font: 9pt Monospace")
