import time
import math
import navpy
import numpy
import cv2
from PyQt5 import QtGui

from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QPolygon, QPixmap
from PyQt5.QtCore import Qt, QPoint

from Widgets.custom_q_widget_base import CustomQWidgetBase
from data_helpers import interpolate, get_value_from_dictionary, distance_between_points
from constants import Constants


class MapWidget(CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None, points_to_keep=200, update_interval=3):
        super().__init__(parent_widget)
        if parent_widget is not None:
            self.setMinimumSize(500, 500)

        self.addSourceKey("vehicle_lat", float, Constants.latitude_key, default_value=0, hide_in_drop_down=True)
        self.addSourceKey("vehicle_lon", float, Constants.longitude_key, default_value=0, hide_in_drop_down=True)
        self.addSourceKey("groundstation_lat", float, Constants.ground_station_latitude_key, default_value=0, hide_in_drop_down=True)
        self.addSourceKey("groundstation_lon", float, Constants.ground_station_longitude_key, default_value=0, hide_in_drop_down=True)

        self.use_ground_station_position = False
        self.gs_lat = 0
        self.gs_lon = 0

        self.map_draw_widget = MapDrawWidget(update_interval)
        self.map_background_widget = MapImageBackground(self)

        layout = QGridLayout()
        layout.setContentsMargins(1, 1, 1, 1)
        # layout.addWidget(self.map_background_widget, 1, 1, 1, 1)
        layout.addWidget(self.map_draw_widget, 1, 1, 1, 1)
        self.setLayout(layout)

        self.datum = []
        self.has_datum = False

        self.map_tile_manager = None

        self.last_image_request_time = time.time()

    def updateData(self, vehicle_data, updated_data):
        heading = float(get_value_from_dictionary(vehicle_data, "yaw", 0))
        latitude = self.getDictValueUsingSourceKey("vehicle_lat")
        longitude = self.getDictValueUsingSourceKey("vehicle_lon")
        gs_lat = self.getValueIfUpdatedUsingSourceKey("groundstation_lat")
        gs_lon = self.getValueIfUpdatedUsingSourceKey("groundstation_lon")

        if Constants.map_tile_manager_key in vehicle_data and self.map_tile_manager is None:
            self.map_tile_manager = vehicle_data[Constants.map_tile_manager_key]

        if gs_lat != 0 and gs_lon != 0:  # Only update the ground station positions when we actually get new data
            self.use_ground_station_position = True
            self.gs_lat = gs_lat
            self.gs_lon = gs_lon
            self.datum = [gs_lat, gs_lon]

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

        self.map_draw_widget.setHeading(heading)

    def updateInFocus(self):
        """Currently handles drawing the background only, but I should move more stuff into here"""
        if len(self.datum) == 0:  # Can't draw a map if we don't know our lat and lon
            return

        if time.time() > self.last_image_request_time + 1 and self.map_tile_manager is not None:  # Do we need a new map?
            self.last_image_request_time = time.time() + 10

            lower_left_coordinates = self.map_draw_widget.drawLocationToPoint(0, self.map_draw_widget.height()) + [0]
            upper_right_coordinates = self.map_draw_widget.drawLocationToPoint(self.map_draw_widget.width(), 0) + [0]

            upper_right_coordinates[0] += 10
            upper_right_coordinates[1] += 10

            lower_left_lla = navpy.ned2lla(lower_left_coordinates, self.datum[0], self.datum[1], 0)
            upper_right_lla = navpy.ned2lla(upper_right_coordinates, self.datum[0], self.datum[1], 0)

            self.map_tile_manager.request_new_tile(lower_left_lla, upper_right_lla)

        if self.map_tile_manager.hasNewMap():  # Check for and get new map if it exists
            map_tile = self.map_tile_manager.getLastTile()

            lower_left_lla = map_tile.lower_left
            upper_right_lla = map_tile.upper_right

            lower_left_coordinates = navpy.lla2ned(lower_left_lla[0], lower_left_lla[1], 0, self.datum[0], self.datum[1], 0)
            upper_right_coordinates = navpy.lla2ned(upper_right_lla[0], upper_right_lla[1], 0, self.datum[0], self.datum[1], 0)

            self.map_background_widget.setMapBackground(map_tile.map_image, lower_left_coordinates[0:2], upper_right_coordinates[0:2])
            self.map_draw_widget.setOpaqueBackground(False)

        map_window_lower_left = self.map_draw_widget.drawLocationToPoint(0, self.map_draw_widget.height())
        map_window_upper_right = self.map_draw_widget.drawLocationToPoint(self.map_draw_widget.width(), 0)
        self.map_background_widget.updateBoundCoordinatesMeters(map_window_lower_left, map_window_upper_right)

    def clearMap(self):
        self.map_draw_widget.clearMap()

    def resetDatum(self):
        self.has_datum = False
        self.clearMap()
        self.use_ground_station_position = False

    def setXY(self, x, y):
        self.map_draw_widget.setXY(x, y)


class MapImageBackground(QLabel):
    def __init__(self, parent=None):
        """Widget that draws the map image background"""
        super().__init__(parent)

        self.map_image = None
        self.map_image_bottom_left = [0, 0]
        self.map_image_top_right = [0, 0]

        self.window_bottom_left = [0, 0]
        self.window_top_right = [0, 0]

    def setMapBackground(self, map_image, bottom_left, upper_right):
        self.map_image = map_image
        self.map_image_bottom_left = bottom_left
        self.map_image_top_right = upper_right

        cv2.imwrite("test.jpg", map_image)

    def updateBoundCoordinatesMeters(self, bottom_left, upper_right, update_background=True):
        self.window_bottom_left = bottom_left
        self.window_top_right = upper_right

        if update_background and self.map_image is not None:
            self.updateImage()

    def updateImage(self):
        map_image_width = self.map_image.shape[0]
        map_image_height = self.map_image.shape[1]

        window_width = self.parent().width()
        window_height = self.parent().height()

        self.move(0, 0)

        image_x_min = math.floor(interpolate(self.window_bottom_left[0], self.map_image_bottom_left[0], self.map_image_top_right[0], 0, map_image_width))
        image_x_max = math.ceil(interpolate(self.window_top_right[0], self.map_image_bottom_left[0], self.map_image_top_right[0], 0, map_image_width))
        image_y_max = math.floor(interpolate(self.window_bottom_left[1], self.map_image_bottom_left[1], self.map_image_top_right[1], map_image_height, 0))  # Y Max to min because matrix rows are numbered top down
        image_y_min = math.ceil(interpolate(self.window_top_right[1], self.map_image_bottom_left[1], self.map_image_top_right[1], map_image_height, 0))

        columns_to_add_left = 0
        columns_to_add_right = 0
        ros_to_add_top = 0
        rows_to_add_bottom = 0

        if image_y_min < 0:
            ros_to_add_top = -image_y_min
            image_y_min = 0
        if image_y_max > map_image_height:
            rows_to_add_bottom = image_y_max - map_image_height
            image_y_max = 0

        if image_x_min < 0:
            columns_to_add_right = -image_x_min
            image_x_min = 0
        if image_x_max > map_image_width:
            columns_to_add_left = image_x_max - map_image_width
            image_x_max = map_image_width

        subset = self.map_image[image_y_min:image_y_max, image_x_min:image_x_max]

        if ros_to_add_top > 0:
            extra_rows_top = numpy.zeros((ros_to_add_top, subset.shape[1], subset.shape[2]), dtype=numpy.uint8)
            subset = numpy.concatenate((extra_rows_top, subset), axis=0)
        if rows_to_add_bottom > 0:
            extra_rows_bottom = numpy.zeros((rows_to_add_bottom, subset.shape[1], subset.shape[2]), dtype=numpy.uint8)
            subset = numpy.concatenate((subset, extra_rows_bottom), axis=0)
        if columns_to_add_left > 0:
            extra_rows_left = numpy.zeros((subset.shape[0], columns_to_add_left, subset.shape[2]), dtype=numpy.uint8)
            subset = numpy.concatenate((subset, extra_rows_left), axis=1)
        if columns_to_add_right > 0:
            extra_rows_right = numpy.zeros((subset.shape[0], columns_to_add_right, subset.shape[2]), dtype=numpy.uint8)
            subset = numpy.concatenate((extra_rows_right, subset), axis=1)

        aspect_ratio = float(subset.shape[0]) / float(subset.shape[1])

        # If the width isn't a multiple of four, bad things happen
        image_width = 4 * round(window_width / 4)
        image_height = window_height  # int(float(image_width) * aspect_ratio)

        self.setMaximumSize(image_width, image_height)
        self.setMinimumSize(image_width, image_height)

        frame = cv2.resize(subset, (int(image_width), int(image_height)))
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        convert_to_qt_format = QtGui.QImage(rgb_image.data, rgb_image.shape[1], rgb_image.shape[0], QtGui.QImage.Format_RGB888)
        convert_to_qt_format = QtGui.QPixmap.fromImage(convert_to_qt_format)
        self.setPixmap(convert_to_qt_format)


class MapDrawWidget(QWidget):
    def __init__(self, update_interval):
        """Widget that draws the arrows and lines on top of the map"""
        super().__init__()
        self.padding = 20
        self.originSize = 20

        self.min_axis_value = -10
        self.max_axis_value = 10

        self.oldPoints = []
        self.paths = {}
        self.opaque_background = True

        self.x_position = 0
        self.y_position = 0
        self.heading = 0

        self.decimals = 0

        self.lastPointTime = time.time()

        self.newPointInterval = update_interval
        self.newPointSpacing = 10

    def setOpaqueBackground(self, enabled):
        self.opaque_background = enabled

    def paintEvent(self, e):
        painter = QPainter(self)  # Blue background
        if self.opaque_background:
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

        out_x = interpolate(x, self.min_axis_value / size_ratio, self.max_axis_value / size_ratio, self.padding + 10, self.width() - self.padding)
        out_y = interpolate(y, self.min_axis_value, self.max_axis_value, self.height() - (self.padding + 10), self.padding)
        return [int(out_x), int(out_y)]

    def drawLocationToPoint(self, x, y):
        """Should be the opposite of the function above"""
        size_ratio = self.height() / self.width()

        out_x = interpolate(x, self.padding + 10, self.width() - self.padding, self.min_axis_value / size_ratio, self.max_axis_value / size_ratio)
        out_y = interpolate(y, self.height() - (self.padding + 10), self.padding, self.min_axis_value, self.max_axis_value)
        return [out_x, out_y]

    def setHeading(self, heading):
        self.heading = heading

    def setXY(self, x, y):
        self.min_axis_value = min(self.min_axis_value, x, y)
        self.max_axis_value = max(self.max_axis_value, x, y)

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

        real_axis_size = self.max_axis_value - self.min_axis_value

        if real_axis_size < 1:
            self.decimals = 2
        elif 1 <= real_axis_size < 20:
            self.decimals = 1
        else:
            self.decimals = 0

    def clearMap(self):
        self.oldPoints = []
        self.paths = {}
