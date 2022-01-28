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

    def updateData(self, vehicleData):
        if self.isHidden():
            return

        if "camera" not in vehicleData:
            self.setMinimumSize(5, 5)
            return
        cameras = vehicleData["camera"]
        if self.videoToUse not in cameras:
            self.setMinimumSize(5, 5)
            return

        frame = cameras[self.videoToUse]

        screenWidth = self.width()
        screenHeight = self.height()

        height = frame.shape[0]
        width = frame.shape[1]
        aspectRatio = float(width) / float(height)
        screenAspectRatio = float(screenWidth) / float(screenHeight)

        # Fix aspect ratio
        if aspectRatio >= screenAspectRatio:
            imageWidth = screenWidth
            imageHeight = int(self.width() / aspectRatio)
        else:
            imageHeight = screenHeight
            imageWidth = int(self.height() * aspectRatio)

        # If the width isn't a multiple of four, bad things happen
        imageWidth = 4 * round(imageWidth / 4)

        # self.setSize(int(imageWidth), int(imageHeight))
        centeredCornerPos = (screenWidth - imageWidth) / 2
        self.videoWidget.move(int(centeredCornerPos), 0)
        self.videoWidget.setMaximumSize(imageWidth, imageHeight)
        self.videoWidget.setMinimumSize(imageWidth, imageHeight)

        # Resize image
        frame = cv2.resize(frame, (int(imageWidth), int(imageHeight)))
        rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        convertToQtFormat = QtGui.QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QtGui.QImage.Format_RGB888)
        convertToQtFormat = QtGui.QPixmap.fromImage(convertToQtFormat)
        self.videoWidget.setPixmap(convertToQtFormat)
