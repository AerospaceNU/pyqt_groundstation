import time
import navpy

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QPolygon
from PyQt5.QtCore import Qt, QPoint

from Widgets.custom_q_widget_base import CustomQWidgetBase
from data_helpers import interpolate, get_value_from_dictionary, distance_between_points
from constants import Constants


class MapWidget(CustomQWidgetBase):
    def __init__(self, parentWidget: QWidget = None, pointsToKeep=200, updateInterval=3):
        super().__init__(parentWidget)
        self.padding = 20
        self.originSize = 20
        self.decimals = 2
        self.paths = {}

        self.pointsToKeep = pointsToKeep
        self.newPointInterval = updateInterval
        self.newPointSpacing = 10
        self.lastPointTime = 0

        self.x_position = 0
        self.y_position = 0
        self.heading = 0
        self.has_datum = False
        self.datum = [0, 0]

        self.maxAxis = 0.1
        self.minAxis = -0.1

        self.oldPoints = []

    def updateData(self, vehicleData):
        if "paths" not in vehicleData:
            paths = {}
        else:
            paths = vehicleData["paths"]

        self.paths = paths

        self.heading = float(get_value_from_dictionary(vehicleData, "yaw", 0))
        latitude = float(get_value_from_dictionary(vehicleData, Constants.latitude_key, 0))
        longitude = float(get_value_from_dictionary(vehicleData, Constants.longitude_key, 0))
        gs_lat = float(get_value_from_dictionary(vehicleData, Constants.ground_station_latitude_key, 0))
        gs_lon = float(get_value_from_dictionary(vehicleData, Constants.ground_station_longitude_key, 0))

        if latitude != 0 and longitude != 0 and gs_lat != 0 and gs_lon != 0:  # If we have rocket lat-lon and gs lat-lon, use that
            ned = navpy.lla2ned(latitude, longitude, 0, gs_lat, gs_lon, 0)
            self.setXY(ned[1], ned[0])
        elif latitude != 0 and longitude != 0:  # If not, use the first rocket position as the datum
            if not self.has_datum:
                self.datum = [latitude, longitude]
                self.has_datum = True

            ned = navpy.lla2ned(latitude, longitude, 0, self.datum[0], self.datum[1], 0)
            self.setXY(ned[1], ned[0])  # ned to enu
        else:  # Otherwise, we're at 0,0
            self.setXY(0, 0)

    def paintEvent(self, e):
        painter = QPainter(self)  # Blue background
        painter.setPen(QPen(QColor(30, 144, 255), 0, Qt.SolidLine))
        painter.setBrush(QBrush(QColor(30, 144, 255), Qt.SolidPattern))
        painter.drawRect(0, 0, self.width(), self.height())

        # Draw paths
        painter.setPen(QPen(QColor(180, 235, 52), 3, Qt.SolidLine))
        for pathName in self.paths:
            path = self.paths[pathName]
            for i in range(len(path) - 1):
                [x1, y1] = path[i]
                [x2, y2] = path[i + 1]

                p1 = self.pointToDrawLocation(x1, y1)
                p2 = self.pointToDrawLocation(x2, y2)
                painter.drawLine(p1[0], p1[1], p2[0], p2[1])

        # Draw old points
        painter.setPen(QPen(QColor(10, 10, 10), 1, Qt.SolidLine))
        for i in range(1, len(self.oldPoints)):
            point = self.oldPoints[i]
            lastPoint = self.oldPoints[i - 1]

            [xPos, yPos] = self.pointToDrawLocation(point[0], point[1])
            [oldX, oldY] = self.pointToDrawLocation(lastPoint[0], lastPoint[1])
            painter.drawLine(int(xPos), int(yPos), oldX, oldY)

        # Draw current position
        [xPos, yPos] = self.pointToDrawLocation(self.x_position, self.y_position)

        if len(self.oldPoints) > 0:
            lastPoint = self.oldPoints[0]
            [oldX, oldY] = self.pointToDrawLocation(lastPoint[0], lastPoint[1])
            painter.drawLine(xPos, yPos, oldX, oldY)

        painter.setPen(QPen(QColor(255, 0, 0), 1, Qt.SolidLine))
        painter.setBrush(QBrush(QColor(255, 0, 0), Qt.SolidPattern))
        points = [QPoint(-6, 10), QPoint(6, 10), QPoint(0, -15)]  # Is a triangle
        poly = QPolygon(points)

        painter.translate(int(xPos), int(yPos))
        painter.rotate(self.heading)
        painter.drawPolygon(poly)
        painter.rotate(-self.heading)
        painter.translate(-int(xPos), -int(yPos))

        # Draw origin axes
        painter.setPen(QPen(QColor(0, 0, 0), 2, Qt.SolidLine))
        [originX, originY] = self.pointToDrawLocation(0, 0)
        painter.drawLine(originX, originY, originX + self.originSize, originY)
        painter.drawLine(originX, originY, originX, originY - self.originSize)

        # Draw X axis
        minXAxis = 0.1 * round(self.minAxis / 0.1) - 1
        maxXAxis = 0.1 * round(self.maxAxis / 0.1) + 1
        [minX, _] = self.pointToDrawLocation(minXAxis, 0)
        [maxX, _] = self.pointToDrawLocation(maxXAxis, 0)
        for x in range(minX, maxX, 50):
            painter.drawLine(x, self.height(), x, self.height() - 10)
            painter.drawLine(0, x, 10, x)

            [xPoint, _] = self.drawLocationToPoint(x, 0)
            if self.decimals == 0:
                xPoint = int(xPoint)
            else:
                xPoint = round(xPoint, self.decimals)

            xPointStr = str(xPoint)
            xOffset = 6 * len(xPointStr) / 2
            painter.drawText(x - xOffset, self.height() - 15, xPointStr)

    def pointToDrawLocation(self, x, y):
        """Converts a point in the real world to a position on the screen"""
        sizeRatio = self.height() / self.width()

        out_x = interpolate(x, self.minAxis / sizeRatio, self.maxAxis / sizeRatio, self.padding + 10, self.width() - self.padding)
        out_y = interpolate(y, self.minAxis, self.maxAxis, self.height() - (self.padding + 10), self.padding)
        return [int(out_x), int(out_y)]

    def drawLocationToPoint(self, x, y):
        """Should be the opposite of the function above"""
        sizeRatio = self.height() / self.width()

        out_x = interpolate(x, self.padding + 10, self.width() - self.padding, self.minAxis / sizeRatio, self.maxAxis / sizeRatio)
        out_y = interpolate(y, self.height() - (self.padding + 10), self.padding, self.minAxis, self.maxAxis)
        return [out_x, out_y]

    def setXY(self, x, y):
        self.maxAxis = max(self.maxAxis, x, y)
        self.minAxis = min(self.minAxis, x, y)

        self.x_position = x
        self.y_position = y

        if len(self.oldPoints) > 0:
            last_point_in_list = self.oldPoints[0]
            distance = distance_between_points(self.x_position, self.y_position, last_point_in_list[0], last_point_in_list[1])
        else:
            distance = 0

        if x == 0:
            return
        if len(self.oldPoints) == 0:
            self.oldPoints = [[x, y]]
        else:
            if time.time() > self.lastPointTime + self.newPointInterval or distance > self.newPointSpacing:
                self.oldPoints = ([[x, y]] + self.oldPoints)  # [:self.pointsToKeep] We keep all the points now
                self.lastPointTime = time.time()

        realAxisSize = self.maxAxis - self.minAxis

        if realAxisSize < 1:
            self.decimals = 2
        elif 1 <= realAxisSize < 20:
            self.decimals = 1
        else:
            self.decimals = 0

    def clearMap(self):
        self.oldPoints = []
        self.maxAxis = 0.1
        self.minAxis = -0.1
        self.paths = {}

    def resetDatum(self):
        self.has_datum = False
        self.clearMap()
