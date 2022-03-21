import numpy as np
import cv2
import imutils

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtGui


class BasicImageDisplay(object):
    def __init__(self, root_widget: QLabel, image, target_width, x=None, y=None):
        """Makes a widget and puts an image in it.  Used to eliminate boilerplate code"""
        self.rootWidget = root_widget
        self.imageWidget = QLabel(root_widget)
        self.rawImage = image
        self.image = None

        self.theta = 0

        self.setGeometry(target_width, x, y)
        self.imageWidget.setStyleSheet("color: black; background: transparent")

    def setGeometry(self, target_width, x=None, y=None):
        window_width = self.rootWidget.width()
        window_height = self.rootWidget.height()

        self.image = imutils.resize(self.rawImage, width=int(target_width))
        height, width, channels = self.image.shape

        if x is None:
            x_offset = int((window_width - width) / 2)
        else:
            x_offset = int(x)

        if y is None:
            y_offset = int((window_height - height) / 2)
        else:
            y_offset = int(y)

        self.imageWidget.setGeometry(x_offset, y_offset, width, height)

        self.updateImage(self.image)

    def setRotation(self, theta):
        img = imutils.rotate(self.image, theta)
        self.updateImage(img)
        self.theta = theta

    def theta(self):
        return self.theta

    def setSingleColor(self, red, green, blue):
        self.image[:, :, 0:3] = np.array([red, green, blue])
        self.rawImage[:, :, 0:3] = np.array([red, green, blue])
        self.updateImage(self.image)

    def updateImage(self, img):
        convert_to_qt_format = QtGui.QImage(img.data, img.shape[1], img.shape[0], QtGui.QImage.Format_ARGB32)
        convert_to_qt_format = QtGui.QPixmap.fromImage(convert_to_qt_format)
        pixmap = QPixmap(convert_to_qt_format)
        self.imageWidget.setPixmap(pixmap)
