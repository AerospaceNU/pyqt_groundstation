"""
Attitude Display
"""
import cv2
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QLabel, QSizePolicy

from Widgets import custom_q_widget_base


class VideoWidget(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, widget: QWidget = None):
        super().__init__(widget)
        self.videoToUse = "webcam"

        self.videoWidget = QLabel(self)

    def setSource(self, source):
        self.videoToUse = source

    def updateData(self, vehicle_data):
        if self.isHidden():
            return

        if "camera" not in vehicle_data:
            self.setMinimumSize(5, 5)
            return
        cameras = vehicle_data["camera"]
        if self.videoToUse not in cameras:
            self.setMinimumSize(5, 5)
            return

        frame = cameras[self.videoToUse]

        screen_width = self.width()
        screen_height = self.height()

        height = frame.shape[0]
        width = frame.shape[1]
        aspect_ratio = float(width) / float(height)
        screen_aspect_ratio = float(screen_width) / float(screen_height)

        # Fix aspect ratio
        if aspect_ratio >= screen_aspect_ratio:
            image_width = screen_width
            image_height = int(self.width() / aspect_ratio)
        else:
            image_height = screen_height
            image_width = int(self.height() * aspect_ratio)

        # If the width isn't a multiple of four, bad things happen
        image_width = 4 * round(image_width / 4)

        # self.setSize(int(image_width), int(image_height))
        centered_corner_pos = (screen_width - image_width) / 2
        self.videoWidget.move(int(centered_corner_pos), 0)
        self.videoWidget.setMaximumSize(image_width, image_height)
        self.videoWidget.setMinimumSize(image_width, image_height)

        # Resize image
        frame = cv2.resize(frame, (int(image_width), int(image_height)))
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        convert_to_qt_format = QtGui.QImage(rgb_image.data, rgb_image.shape[1], rgb_image.shape[0], QtGui.QImage.Format_RGB888)
        convert_to_qt_format = QtGui.QPixmap.fromImage(convert_to_qt_format)
        self.videoWidget.setPixmap(convert_to_qt_format)
