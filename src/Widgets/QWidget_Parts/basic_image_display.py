import imutils
import numpy as np
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel


class BasicImageDisplay(QLabel):
    def __init__(self, image, target_width, parent=None, x=None, y=None):
        """Makes a widget and puts an image in it.  Used to eliminate boilerplate code"""
        super().__init__(parent)

        self.rawImage = image
        self.image = None

        self.theta = 0

        self.setTargetWidth(target_width, x, y)
        self.setStyleSheet("color: black; background: transparent")

    def setTargetWidth(self, target_width, x=None, y=None):
        self.image = imutils.resize(self.rawImage, width=int(target_width))
        height, width, channels = self.image.shape

        if x is None:
            if self.parent() is not None:
                x_offset = int((self.parent().width() - width) / 2)
            else:
                x_offset = 0
        else:
            x_offset = int(x)

        if y is None:
            if self.parent() is not None:
                y_offset = int((self.parent().height() - height) / 2)
            else:
                y_offset = 0
        else:
            y_offset = int(y)

        self.setGeometry(x_offset, y_offset, width, height)

        self.updateImage(self.image)

    def setRotation(self, theta):
        img = imutils.rotate(self.image, theta)
        self.updateImage(img)
        self.theta = theta

    def theta(self):
        return self.theta

    def setSingleColor(self, red, green, blue):
        self.image[:, :, 0:3] = np.array([blue, green, red])
        self.rawImage[:, :, 0:3] = np.array([blue, green, red])
        self.updateImage(self.image)

    def updateImage(self, img):
        convert_to_qt_format = QtGui.QImage(img.data, img.shape[1], img.shape[0], QtGui.QImage.Format_ARGB32)
        convert_to_qt_format = QtGui.QPixmap.fromImage(convert_to_qt_format)
        pixmap = QPixmap(convert_to_qt_format)
        self.setPixmap(pixmap)
