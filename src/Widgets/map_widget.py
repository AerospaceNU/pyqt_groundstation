import math
import time

import cv2
import navpy
import numpy
from PyQt5 import QtGui
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QMouseEvent, QPainter, QPen, QPolygon
from PyQt5.QtWidgets import QGridLayout, QLabel, QMenu, QWidget

from src.constants import Constants
from src.data_helpers import (
    distance_between_points,
    get_value_from_dictionary,
    interpolate,
)
from src.Widgets.custom_q_widget_base import CustomQWidgetBase

BACKGROUND_COLOR = (255, 144, 30)  # BGR for OpenCV

EXTRA_POSITION_SOURCES = {"egg_finder": [Constants.egg_finder_latitude, Constants.egg_finder_longitude]}


class MapWidget(CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None, points_to_keep=200, update_interval=3):
        super().__init__(parent_widget)
        if parent_widget is not None:
            self.setMinimumSize(500, 500)

        self.addSourceKey("groundstation_lat", float, Constants.ground_station_latitude_key, default_value=0, hide_in_drop_down=True)
        self.addSourceKey("groundstation_lon", float, Constants.ground_station_longitude_key, default_value=0, hide_in_drop_down=True)
        self.addSourceKey("vehicle_lat", float, Constants.latitude_key, default_value=0, hide_in_drop_down=True)
        self.addSourceKey("vehicle_lon", float, Constants.longitude_key, default_value=0, hide_in_drop_down=True)

        for source in EXTRA_POSITION_SOURCES:
            self.addSourceKey("{}_lat".format(source), float, EXTRA_POSITION_SOURCES[source][0], default_value=0, hide_in_drop_down=True)
            self.addSourceKey("{}_lon".format(source), float, EXTRA_POSITION_SOURCES[source][1], default_value=0, hide_in_drop_down=True)

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

    def addCustomMenuItems(self, menu: QMenu, e):
        menu.addAction("Clear Map", self.clearMap)
        menu.addAction("Reset Datum", self.resetDatum)
        menu.addAction("Reset Origin", self.resetOrigin)

        if self.map_draw_widget.dragging_enabled:
            menu.addAction("Disable Map Dragging", lambda enabled=False: self.map_draw_widget.setDraggingEnabled(enabled))
        else:
            menu.addAction("Enable Map Dragging", lambda enabled=True: self.map_draw_widget.setDraggingEnabled(enabled))

    def updateData(self, vehicle_data, updated_data):
        heading = float(get_value_from_dictionary(vehicle_data, Constants.yaw_position_key, 0))
        gs_lat = self.getValueIfUpdatedUsingSourceKey("groundstation_lat")
        gs_lon = self.getValueIfUpdatedUsingSourceKey("groundstation_lon")
        latitude = self.getDictValueUsingSourceKey("vehicle_lat")
        longitude = self.getDictValueUsingSourceKey("vehicle_lon")

        if Constants.map_tile_manager_key in vehicle_data and self.map_tile_manager is None:
            self.map_tile_manager = vehicle_data[Constants.map_tile_manager_key]

        if gs_lat != 0 and gs_lon != 0:  # Only update the ground station positions when we actually get new data
            self.use_ground_station_position = True
            self.gs_lat = gs_lat
            self.gs_lon = gs_lon
            self.datum = [gs_lat, gs_lon]
            self.has_datum = True

        if latitude != 0 and longitude != 0 and self.use_ground_station_position:  # If we have rocket lat-lon and gs lat-lon, use that
            ned = navpy.lla2ned(latitude, longitude, 0, self.gs_lat, self.gs_lon, 0)
            self.map_draw_widget.setXY(ned[1], ned[0])
        elif latitude != 0 and longitude != 0:  # If not, use the first rocket position as the datum
            if not self.has_datum:
                self.datum = [latitude, longitude]
                self.has_datum = True

            ned = navpy.lla2ned(latitude, longitude, 0, self.datum[0], self.datum[1], 0)
            self.map_draw_widget.setXY(ned[1], ned[0])  # ned to enu
        else:  # Otherwise, we're at 0,0
            self.map_draw_widget.setXY(0, 0)

        for source in EXTRA_POSITION_SOURCES:
            lat = self.getValueIfUpdatedUsingSourceKey("{}_lat".format(source))
            lon = self.getValueIfUpdatedUsingSourceKey("{}_lon".format(source))
            if lat == 0 or lon == 0:
                continue

            if not self.has_datum:
                self.datum = [lat, lon]
                self.has_datum = True

            if self.has_datum:
                ned = navpy.lla2ned(lat, lon, 0, self.datum[0], self.datum[1], 0)
                self.map_draw_widget.setXY(ned[1], ned[0], position_name=source)

        self.map_draw_widget.setHeading(heading)

    def updateInFocus(self):
        """Currently handles drawing the background only, but I should move more stuff into here"""
        if len(self.datum) == 0:  # Can't draw a map if we don't know our lat and lon
            return

        if time.time() > self.last_image_request_time + 5 and self.map_tile_manager is not None:  # Do we need a new map?
            self.last_image_request_time = time.time()

            lower_left_coordinates = self.map_draw_widget.drawLocationToPoint(0, self.map_draw_widget.height())
            upper_right_coordinates = self.map_draw_widget.drawLocationToPoint(self.map_draw_widget.width(), 0)

            lower_left_ned = [lower_left_coordinates[1], lower_left_coordinates[0], 0]
            upper_right_ned = [upper_right_coordinates[1], upper_right_coordinates[0], 0]

            lower_left_lla = navpy.ned2lla(lower_left_ned, self.datum[0], self.datum[1], 0)
            upper_right_lla = navpy.ned2lla(upper_right_ned, self.datum[0], self.datum[1], 0)

            self.map_tile_manager.request_new_tile(lower_left_lla, upper_right_lla, self.width())

        if self.map_tile_manager is not None and self.map_tile_manager.hasNewMap():  # Check for and get new map if it exists
            map_tile = self.map_tile_manager.getLastTile()

            lower_left_lla = map_tile.lower_left
            upper_right_lla = map_tile.upper_right

            lower_left_coordinates = navpy.lla2ned(lower_left_lla[0], lower_left_lla[1], 0, self.datum[0], self.datum[1], 0)
            upper_right_coordinates = navpy.lla2ned(upper_right_lla[0], upper_right_lla[1], 0, self.datum[0], self.datum[1], 0)

            lower_left_enu = [lower_left_coordinates[1], lower_left_coordinates[0]]
            upper_right_enu = [upper_right_coordinates[1], upper_right_coordinates[0]]

            self.map_background_widget.setMapBackground(map_tile.map_image, lower_left_enu, upper_right_enu)
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
        self.map_background_widget.removeMapBackground()
        self.map_draw_widget.setOpaqueBackground(True)
        self.last_image_request_time = 0  # Request new map now

    def resetOrigin(self):
        self.map_draw_widget.resetOrigin()


class MapImageBackground(QLabel):
    def __init__(self, parent=None):
        """Widget that draws the map image background"""
        super().__init__(parent)

        self.has_new_map_image = True
        self.map_image = None
        self.initial_draw_passes = 0
        self.map_image_bottom_left = [0, 0]
        self.map_image_top_right = [0, 0]

        self.window_bottom_left = [0, 0]
        self.window_top_right = [0, 0]

        self.last_map_bl = [0, 0]
        self.last_map_ur = [0, 0]
        self.last_window_bl = [0, 0]
        self.last_window_ur = [0, 0]

        self.setStyleSheet("color: black")

    def setMapBackground(self, map_image, bottom_left, upper_right):
        self.map_image = map_image
        self.map_image_bottom_left = bottom_left
        self.map_image_top_right = upper_right
        self.has_new_map_image = True

    def removeMapBackground(self):
        self.map_image = None
        self.map_image_bottom_left = [0, 0]
        self.map_image_top_right = [0, 0]

        self.window_bottom_left = [0, 0]
        self.window_top_right = [0, 0]

        self.initial_draw_passes = 0

    def updateBoundCoordinatesMeters(self, bottom_left, upper_right, update_background=True):
        self.window_bottom_left = bottom_left
        self.window_top_right = upper_right

        if update_background and self.map_image is not None:
            self.updateImage()

    def isMapSameAsLast(self):
        map_ur_same = self.last_map_ur == self.map_image_top_right
        map_bl_same = self.last_map_bl == self.map_image_bottom_left
        win_ur_same = self.last_window_ur == self.window_top_right
        win_bl_same = self.last_window_bl == self.window_bottom_left

        is_map_same = map_ur_same and map_bl_same and win_ur_same and win_bl_same and not self.has_new_map_image

        self.has_new_map_image = False
        self.last_map_ur = self.map_image_top_right
        self.last_map_bl = self.map_image_bottom_left
        self.last_window_ur = self.window_top_right
        self.last_window_bl = self.window_bottom_left

        return is_map_same

    def updateImage(self):
        if self.initial_draw_passes < 2:  # We need to draw the map twice the first time for some reason
            self.initial_draw_passes += 1
        elif self.isMapSameAsLast():
            return

        map_image_width = self.map_image.shape[1]
        map_image_height = self.map_image.shape[0]

        window_width = self.parent().width()
        window_height = self.parent().height()

        self.move(0, 0)

        # Make sure the map actually goes on the screen
        if self.map_image_bottom_left[0] > self.window_top_right[0]:
            return
        elif self.map_image_top_right[0] < self.window_bottom_left[0]:
            return
        elif self.map_image_bottom_left[1] > self.window_top_right[1]:
            return
        elif self.map_image_top_right[1] < self.window_bottom_left[1]:
            return

        image_x_min = math.floor(interpolate(self.window_bottom_left[0], self.map_image_bottom_left[0], self.map_image_top_right[0], 0, map_image_width))
        image_x_max = math.ceil(interpolate(self.window_top_right[0], self.map_image_bottom_left[0], self.map_image_top_right[0], 0, map_image_width))
        image_y_max = math.floor(interpolate(self.window_bottom_left[1], self.map_image_bottom_left[1], self.map_image_top_right[1], map_image_height, 0))  # Y Max to min because matrix rows are numbered top down
        image_y_min = math.ceil(interpolate(self.window_top_right[1], self.map_image_bottom_left[1], self.map_image_top_right[1], map_image_height, 0))

        subset_width_pixels = image_x_max - image_x_min
        width_ratio = self.width() / subset_width_pixels

        columns_to_add_left = 0
        columns_to_add_right = 0
        rows_to_add_top = 0
        rows_to_add_bottom = 0

        if image_y_min < 0:
            rows_to_add_top = -image_y_min
            image_y_min = 0
        if image_y_max > map_image_height:
            rows_to_add_bottom = image_y_max - map_image_height
            image_y_max = map_image_height

        if image_x_min < 0:
            columns_to_add_right = -image_x_min
            image_x_min = 0
        if image_x_max > map_image_width:
            columns_to_add_left = image_x_max - map_image_width
            image_x_max = map_image_width

        # Do the resize before we add extra pixels
        subset = self.map_image[image_y_min:image_y_max, image_x_min:image_x_max]

        new_width = int(float(subset.shape[1]) * width_ratio)
        new_height = int(float(subset.shape[0]) * width_ratio)

        if new_width > 0 and new_height > 0:
            subset = cv2.resize(subset, (new_width, new_height))

            ros_to_add_top = int(rows_to_add_top * width_ratio)
            rows_to_add_bottom = int(rows_to_add_bottom * width_ratio)
            columns_to_add_left = int(columns_to_add_left * width_ratio)
            columns_to_add_right = int(columns_to_add_right * width_ratio)

            if ros_to_add_top > 0:
                extra_rows_top = numpy.zeros((ros_to_add_top, subset.shape[1], subset.shape[2]), dtype=numpy.uint8)
                extra_rows_top[:] = BACKGROUND_COLOR
                subset = numpy.concatenate((extra_rows_top, subset), axis=0)
            if rows_to_add_bottom > 0:
                extra_rows_bottom = numpy.zeros((rows_to_add_bottom, subset.shape[1], subset.shape[2]), dtype=numpy.uint8)
                extra_rows_bottom[:] = BACKGROUND_COLOR
                subset = numpy.concatenate((subset, extra_rows_bottom), axis=0)
            if columns_to_add_left > 0:
                extra_rows_left = numpy.zeros((subset.shape[0], columns_to_add_left, subset.shape[2]), dtype=numpy.uint8)
                extra_rows_left[:] = BACKGROUND_COLOR
                subset = numpy.concatenate((subset, extra_rows_left), axis=1)
            if columns_to_add_right > 0:
                extra_rows_right = numpy.zeros((subset.shape[0], columns_to_add_right, subset.shape[2]), dtype=numpy.uint8)
                extra_rows_right[:] = BACKGROUND_COLOR
                subset = numpy.concatenate((extra_rows_right, subset), axis=1)
        else:
            subset = numpy.zeros((100, 100, 3), dtype=numpy.uint8)
            subset[:] = BACKGROUND_COLOR

        self.setMaximumSize(window_width, window_height)
        self.setMinimumSize(window_width, window_height)

        rgb_image = cv2.cvtColor(subset, cv2.COLOR_BGR2RGBA)
        convert_to_qt_format = QtGui.QImage(rgb_image.data, rgb_image.shape[1], rgb_image.shape[0], QtGui.QImage.Format_RGBA8888)
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

        self.origin_offset_meters = [0, 0]

        self.oldPoints = []
        self.paths = {}
        self.opaque_background = True

        self.position_dict = {}

        self.heading = 0

        self.decimals = 0

        self.lastPointTime = time.time()

        self.newPointInterval = update_interval
        self.newPointSpacing = 10

        self.isClicked = False
        self.activeOffset = [0, 0]
        self.dragging_enabled = False

    def setOpaqueBackground(self, enabled):
        self.opaque_background = enabled

    def setDraggingEnabled(self, enabled):
        self.dragging_enabled = enabled

    def wheelEvent(self, event):
        if not self.dragging_enabled:
            super(MapDrawWidget, self).wheelEvent(event)
            return

        scroll_distance = -event.angleDelta().y()
        delta_meters = (self.max_axis_value - self.min_axis_value) / 10

        self.min_axis_value = min(self.min_axis_value - (delta_meters * scroll_distance / 120.0), -10)  # 120 is a magic number based on how far the mouse goes
        self.max_axis_value = max(self.max_axis_value + (delta_meters * scroll_distance / 120.0), 10)

    def mousePressEvent(self, e: QMouseEvent):
        """Determines if we clicked on a widget"""
        if not self.dragging_enabled:
            super(MapDrawWidget, self).mousePressEvent(e)
            return

        self.isClicked = True
        self.activeOffset = [e.screenPos().x(), e.screenPos().y()]

    def mouseMoveEvent(self, e: QMouseEvent):
        """Moves the active widget to the position of the mouse if we are currently clicked"""
        if not self.dragging_enabled:
            super().mouseMoveEvent(e)
            return

        meters_per_pixel = (self.max_axis_value - self.min_axis_value) / self.height()

        if self.isClicked:
            self.origin_offset_meters[0] += (e.screenPos().x() - self.activeOffset[0]) * meters_per_pixel
            self.origin_offset_meters[1] -= (e.screenPos().y() - self.activeOffset[1]) * meters_per_pixel
            self.activeOffset = [e.screenPos().x(), e.screenPos().y()]

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        if not self.dragging_enabled:
            super().mouseReleaseEvent(a0)
            return

        self.isClicked = False

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

        # Draw current positions

        for position in self.position_dict:
            [xPos, yPos] = self.pointToDrawLocation(self.position_dict[position][0], self.position_dict[position][1])

            if len(self.oldPoints) > 0 and position == "default":
                painter.setPen(QPen(QColor(10, 10, 10), 1, Qt.SolidLine))
                lastPoint = self.oldPoints[0]
                [oldX, oldY] = self.pointToDrawLocation(lastPoint[0], lastPoint[1])
                painter.drawLine(int(xPos), int(yPos), int(oldX), int(oldY))

            if position == "default":
                painter.setPen(QPen(QColor(255, 0, 0), 1, Qt.SolidLine))
                painter.setBrush(QBrush(QColor(255, 0, 0), Qt.SolidPattern))
            else:
                painter.setPen(QPen(QColor(0, 255, 0), 1, Qt.SolidLine))
                painter.setBrush(QBrush(QColor(0, 255, 0), Qt.SolidPattern))

            points = [QPoint(-6, 10), QPoint(6, 10), QPoint(0, -15)]  # Is a triangle
            poly = QPolygon(points)

            heading = -self.heading + 90  # Translate to coordinates that we can use on the screen

            painter.translate(int(xPos), int(yPos))
            painter.rotate(heading)
            painter.drawPolygon(poly)
            painter.rotate(-heading)
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

        out_x = interpolate(x, (self.min_axis_value / size_ratio) - self.origin_offset_meters[0], (self.max_axis_value / size_ratio) - self.origin_offset_meters[0], self.padding + 10, self.width() - self.padding)
        out_y = interpolate(y, self.min_axis_value - self.origin_offset_meters[1], self.max_axis_value - self.origin_offset_meters[1], self.height() - (self.padding + 10), self.padding)
        return [int(out_x), int(out_y)]

    def drawLocationToPoint(self, x, y):
        """Should be the opposite of the function above"""
        size_ratio = self.height() / self.width()

        out_x = interpolate(x, self.padding + 10, self.width() - self.padding, (self.min_axis_value / size_ratio) - self.origin_offset_meters[0], (self.max_axis_value / size_ratio) - self.origin_offset_meters[0])
        out_y = interpolate(y, self.height() - (self.padding + 10), self.padding, self.min_axis_value - self.origin_offset_meters[1], self.max_axis_value - self.origin_offset_meters[1])
        return [out_x, out_y]

    def setHeading(self, heading):
        self.heading = heading

    def setXY(self, x, y, position_name="default"):
        # Track smallest and largest value ever seen
        self.min_axis_value = min(self.min_axis_value, x, y)
        self.max_axis_value = max(self.max_axis_value, x, y)

        # Update current position of vehicle
        self.position_dict[position_name] = [x, y]

        if position_name != "default":
            return

        # Get distance to last point in history
        if len(self.oldPoints) > 0:
            last_point_in_list = self.oldPoints[0]
            distance = distance_between_points(x, y, last_point_in_list[0], last_point_in_list[1])
        else:
            distance = 0

        # Update history if we need to
        if x == 0:
            return
        if len(self.oldPoints) == 0:
            self.oldPoints = [[x, y]]
        else:
            if time.time() > self.lastPointTime + self.newPointInterval or distance > self.newPointSpacing:
                self.oldPoints = [[x, y]] + self.oldPoints
                # [:self.pointsToKeep] We keep all the points now
                self.lastPointTime = time.time()

        # Figure out how many decimals to use on the axis scales
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
        self.min_axis_value = -10
        self.max_axis_value = 10

        self.origin_offset_meters = [0, 0]

    def resetOrigin(self):
        self.origin_offset_meters = [0, 0]
