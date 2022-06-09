"""
Widget for downloading maps
"""
import time

import cv2
from PyQt5 import QtGui
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from src.constants import Constants
from src.Widgets import custom_q_widget_base


class MapDownload(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, widget: QWidget = None):
        super().__init__(widget)

        self.titleWidget = QLabel()
        self.mapDisplay = QLabel()
        self.downloadButton = QPushButton()

        layout = QVBoxLayout()
        layout.addWidget(self.titleWidget)
        layout.addWidget(self.mapDisplay)
        layout.addWidget(self.downloadButton)
        self.setLayout(layout)

        self.titleWidget.setText("Map Download Widget")
        self.downloadButton.setText("Download")

        self.downloadButton.clicked.connect(self.onButtonClick)

        self.map_tile_manager = None

        self.lastUpdateTime = 0

        self.lowerLeft = None
        self.upperRight = None

    def updateData(self, vehicle_data, updated_data):
        if Constants.map_tile_manager_key in vehicle_data and self.map_tile_manager is None:
            self.map_tile_manager = vehicle_data[Constants.map_tile_manager_key]

        if self.map_tile_manager is not None:
            map_image_object = self.map_tile_manager.peekNewestTile()

            if map_image_object is not None and time.time() > self.lastUpdateTime + 5:
                map_image = map_image_object.map_image
                self.lowerLeft = map_image_object.lower_left
                self.upperRight = map_image_object.upper_right

                ratio = float(map_image.shape[1]) / float(map_image.shape[0])
                new_width = 300
                new_height = int(new_width * ratio)

                map_image = cv2.resize(map_image, (new_height, new_width))

                rgb_image = cv2.cvtColor(map_image, cv2.COLOR_BGR2RGBA)
                convert_to_qt_format = QtGui.QImage(rgb_image.data, rgb_image.shape[1], rgb_image.shape[0], QtGui.QImage.Format_RGBA8888)
                convert_to_qt_format = QtGui.QPixmap.fromImage(convert_to_qt_format)
                self.mapDisplay.setPixmap(convert_to_qt_format)

    def onButtonClick(self):
        if self.map_tile_manager is not None:
            self.map_tile_manager.request_tile_download(self.lowerLeft, self.upperRight)
