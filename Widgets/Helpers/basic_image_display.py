import numpy as np
import cv2
import imutils
import self as self

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtGui


class BasicImageDisplay(object):
    def __init__(self, rootWidget: QLabel, image, targetWidth, x=None, y=None):
        """Makes a widget and puts an image in it.  Used to eliminate boilerplate code"""
        self.rootWidget = rootWidget
        self.imageWidget = QLabel(rootWidget)
        self.rawImage = image
        self.image = None

        self.theta = 0

        self.setGeometry(targetWidth, x, y)

    def setGeometry(self, targetWidth, x=None, y=None):
        windowWidth = self.rootWidget.width()
        windowHeight = self.rootWidget.height()

        self.image = imutils.resize(self.rawImage, width=int(targetWidth))
        height, width, channels = self.image.shape

        if x is None:
            xOffset = int((windowWidth - width) / 2)
        else:
            xOffset = int(x)

        if y is None:
            yOffset = int((windowHeight - height) / 2)
        else:
            yOffset = int(y)

        self.imageWidget.setGeometry(xOffset, yOffset, width, height)

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
        convertToQtFormat = QtGui.QImage(img.data, img.shape[1], img.shape[0], QtGui.QImage.Format_ARGB32)
        convertToQtFormat = QtGui.QPixmap.fromImage(convertToQtFormat)
        pixmap = QPixmap(convertToQtFormat)
        self.imageWidget.setPixmap(pixmap)
