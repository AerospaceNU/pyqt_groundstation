import os

import cv2
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPolygon, QRegion
from PyQt5.QtWidgets import QLabel, QWidget

from src.Widgets.QWidget_Parts import basic_image_display


class AttitudeDisplayWidget(QLabel):
    def __init__(self, parent_widget: QWidget = None):
        super().__init__(parent_widget)

        self.size = 200

        self.setGeometry(0, 0, 200, 200)

        self.roll = 0
        self.pitch = 0

        dir_name = os.path.dirname(__file__)
        dir_name = os.path.abspath(os.path.join(dir_name, "../.."))
        self.crossHair = cv2.imread("{}/Assets/cross_hair.png".format(dir_name), cv2.IMREAD_UNCHANGED)
        self.rollPointer = cv2.imread("{}/Assets/roll_pointer.png".format(dir_name), cv2.IMREAD_UNCHANGED)
        self.rollIndicator = cv2.imread("{}/Assets/roll_dial_1.png".format(dir_name), cv2.IMREAD_UNCHANGED)

        # Cross-hair
        self.crossHairImage = basic_image_display.BasicImageDisplay(self.crossHair, int(self.size * 0.7), parent=self)
        self.rollPointerImage = basic_image_display.BasicImageDisplay(self.rollPointer, self.size * 0.05, y=10, parent=self)
        self.rollIndicatorImage = basic_image_display.BasicImageDisplay(self.rollIndicator, self.size * 0.9, parent=self)

        self.refreshMask()

    def setSize(self, size):
        # TODO: Use the QWidget size functions instead of this sketchy one
        self.size = size

        self.setGeometry(0, 0, size, size)
        self.setMinimumWidth(size)
        self.setMaximumWidth(size)
        self.setMinimumHeight(size)
        self.setMaximumHeight(size)
        self.refreshMask()

        self.crossHairImage.setTargetWidth(size * 0.7)
        self.rollPointerImage.setTargetWidth(size * 0.05, y=10)
        self.rollIndicatorImage.setTargetWidth(size * 0.9)

    def refreshMask(self):
        # Set up octagonal mask for painter
        corner_size = int(self.width() / 8)
        points = [
            QPoint(corner_size, 0),
            QPoint(0, corner_size),
            QPoint(0, self.height() - corner_size),
            QPoint(corner_size, self.height()),
            QPoint(self.width() - corner_size, self.height()),
            QPoint(self.width(), self.height() - corner_size),
            QPoint(self.height(), corner_size),
            QPoint(self.height() - corner_size, 0),
        ]
        poly = QPolygon(points)
        region = QRegion(poly)
        self.setMask(region)

    def paintEvent(self, e):
        # Horizon green rectangle
        r = self.size * 2  # Rectangle width
        r2 = self.size * 2  # Rectangle height

        painter = QPainter(self)  # Blue background
        painter.setPen(QPen(QColor(30, 144, 255), 0, Qt.SolidLine))
        painter.setBrush(QBrush(QColor(30, 144, 255), Qt.SolidPattern))
        painter.drawRect(0, 0, self.width(), self.height())

        painter.setPen(QPen(QColor(166, 99, 0), 0, Qt.SolidLine))  # Brown horizon
        painter.setBrush(QBrush(QColor(166, 99, 0), Qt.SolidPattern))

        center_x = int(self.width() / 2)
        center_y = int(self.height() / 2)
        pitch_scale_factor = (-1 / 50) * (self.height() / 2)

        painter.translate(
            center_x, center_y
        )  # Set our coordinate system to be centered on the widget
        painter.rotate(-self.roll)

        painter.drawRect(-r, pitch_scale_factor * self.pitch, 2 * r, r2)

        # Pitch marker
        line_width = int(self.width() / 200)
        font_size = max(int(self.width() / 30), 8)
        short_length = self.width() / 8
        long_length = self.width() / 4

        painter.setPen(QPen(Qt.white, line_width, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))

        spacing = 5  # Draw lines every 5 degrees
        nearest_pitch = spacing * round(self.pitch / spacing)
        max_to_draw_line = int(
            abs((self.width() * 0.5) / (2 * pitch_scale_factor))
        )  # Figure out the biggest pitch to get a line drawn
        max_pitch = min(nearest_pitch + max_to_draw_line + spacing, 91)
        min_pitch = max(nearest_pitch - max_to_draw_line, -90)

        for i in range(min_pitch, max_pitch, spacing):
            nearest_pitch_delta = (self.pitch - i) * pitch_scale_factor

            if i % 10 != 0:
                painter.drawLine(
                    -short_length / 2,
                    nearest_pitch_delta,
                    short_length / 2,
                    nearest_pitch_delta,
                )
                text_distance = short_length / 2
            else:
                painter.drawLine(
                    -long_length / 2,
                    nearest_pitch_delta,
                    long_length / 2,
                    nearest_pitch_delta,
                )
                text_distance = long_length / 2

            painter.setFont(QFont("Helvetica", font_size))
            painter.drawText(
                text_distance * 1.1,
                nearest_pitch_delta + int(font_size / 2),
                "{}".format(abs(i)),
            )
            painter.drawText(
                -(text_distance * 1.1 + (font_size - 2) * 2),
                nearest_pitch_delta + int(font_size / 2),
                "{:2}".format(abs(i)),
            )

        self.rollIndicatorImage.setRotation(self.roll)  # Set roll image

    def setRPY(self, roll, pitch, _):
        if pitch > 180:
            pitch -= 360

        self.roll = roll
        self.pitch = pitch
