import time
import navpy

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QPolygon
from PyQt5.QtCore import Qt, QPoint

from Widgets.custom_q_widget_base import CustomQWidgetBase
from data_helpers import interpolate, get_value_from_dictionary, distance_between_points
from constants import Constants


class MapWidget(CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None, points_to_keep=200, update_interval=3):
        super().__init__(parent_widget)
        self.padding = 20
        self.originSize = 20
        self.decimals = 2
        self.paths = {}

        if parent_widget is not None:
            self.setMinimumSize(500, 500)

        self.addSourceKey("vehicle_lat", float, Constants.latitude_key, default_value=0, hide_in_drop_down=True)
        self.addSourceKey("vehicle_lon", float, Constants.longitude_key, default_value=0, hide_in_drop_down=True)
        self.addSourceKey("groundstation_lat", float, Constants.ground_station_latitude_key, default_value=0, hide_in_drop_down=True)
        self.addSourceKey("groundstation_lon", float, Constants.ground_station_longitude_key, default_value=0, hide_in_drop_down=True)

        self.use_ground_station_position = False
        self.gs_lat = 0
        self.gs_lon = 0
        self.pointsToKeep = points_to_keep
        self.newPointInterval = update_interval
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

    def updateData(self, vehicle_data, updated_data):
        if "paths" not in vehicle_data:
            paths = {}
        else:
            paths = vehicle_data["paths"]

        self.paths = paths

        self.heading = float(get_value_from_dictionary(vehicle_data, "yaw", 0))
        latitude = self.getDictValueUsingSourceKey("vehicle_lat")
        longitude = self.getDictValueUsingSourceKey("vehicle_lon")
        gs_lat = self.getValueIfUpdatedUsingSourceKey("groundstation_lat")
        gs_lon = self.getValueIfUpdatedUsingSourceKey("groundstation_lon")

        if gs_lat != 0 and gs_lon != 0:  # Only update the ground station positions when we actually get new data
            self.use_ground_station_position = True
            self.gs_lat = gs_lat
            self.gs_lon = gs_lon

        if latitude != 0 and longitude != 0 and self.use_ground_station_position:  # If we have rocket lat-lon and gs lat-lon, use that
            ned = navpy.lla2ned(latitude, longitude, 0, self.gs_lat, self.gs_lon, 0)
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
            painter.drawLine(int(xPos), int(yPos), int(oldX), int(oldY))

        # Draw current position
        [xPos, yPos] = self.pointToDrawLocation(self.x_position, self.y_position)

        if len(self.oldPoints) > 0:
            lastPoint = self.oldPoints[0]
            [oldX, oldY] = self.pointToDrawLocation(lastPoint[0], lastPoint[1])
            painter.drawLine(int(xPos), int(yPos), int(oldX), int(oldY))

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
        line_spacing_px = 60
        number_of_lines_to_draw = int(self.width() / line_spacing_px) + 1

        for i in range(-number_of_lines_to_draw, number_of_lines_to_draw):
            x = i * line_spacing_px + originX

            painter.drawLine(x, self.height(), x, self.height() - 10)
            # painter.drawLine(0, x, 10, x)

            [xPoint, _] = self.drawLocationToPoint(x, 0)
            if self.decimals == 0:
                xPoint = int(xPoint)
            else:
                xPoint = round(xPoint, self.decimals)

            xPointStr = str(xPoint)
            xOffset = 6 * len(xPointStr) / 2
            painter.drawText(x - xOffset, self.height() - 15, xPointStr)

        number_of_y_lines_to_draw = int(self.height() / line_spacing_px) + 1
        for i in range(-number_of_y_lines_to_draw, number_of_y_lines_to_draw):
            y = i * line_spacing_px + originY
            painter.drawLine(0, y, 10, y)

            [_, y_label] = self.drawLocationToPoint(0, y)

            if self.decimals == 0:
                y_label = int(y_label)
            else:
                y_label = round(y_label, self.decimals)

            text_y_offset = self.fontInfo().pixelSize() / 3
            painter.drawText(15, y + text_y_offset, str(y_label))

    def pointToDrawLocation(self, x, y):
        """Converts a point in the real world to a position on the screen"""
        size_ratio = self.height() / self.width()

        out_x = interpolate(x, self.minAxis / size_ratio, self.maxAxis / size_ratio, self.padding + 10, self.width() - self.padding)
        out_y = interpolate(y, self.minAxis, self.maxAxis, self.height() - (self.padding + 10), self.padding)
        return [int(out_x), int(out_y)]

    def drawLocationToPoint(self, x, y):
        """Should be the opposite of the function above"""
        size_ratio = self.height() / self.width()

        out_x = interpolate(x, self.padding + 10, self.width() - self.padding, self.minAxis / size_ratio, self.maxAxis / size_ratio)
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

        real_axis_size = self.maxAxis - self.minAxis

        if real_axis_size < 1:
            self.decimals = 2
        elif 1 <= real_axis_size < 20:
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
        self.use_ground_station_position = False
