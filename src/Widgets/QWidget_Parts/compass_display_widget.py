import os

import cv2
from PyQt5.QtWidgets import QLabel, QWidget

from src.data_helpers import get_rgb_from_string
from src.Widgets.QWidget_Parts import basic_image_display


class CompassDisplayWidget(QLabel):
    def __init__(self, parentWidget: QWidget = None):
        super().__init__(parentWidget)
        self.size = 200

        dirName = os.path.dirname(__file__)
        dirName = os.path.abspath(os.path.join(dirName, "../.."))
        compass = cv2.imread("{}/Assets/compass.png".format(dirName), cv2.IMREAD_UNCHANGED)
        arrowImg = cv2.resize(cv2.imread("{}/Assets/arrow.png".format(dirName), cv2.IMREAD_UNCHANGED)[900:2100, 900:2100], (self.size, int(self.size / 2)), )

        self.compassImage = basic_image_display.BasicImageDisplay(compass, self.size, parent=self)
        self.arrowImage = basic_image_display.BasicImageDisplay(arrowImg, self.size, parent=self)

    def setYaw(self, yaw):
        yaw = yaw + 180
        self.arrowImage.setRotation(yaw)

    def setSize(self, size):
        # TODO: Use the QWidget size functions instead of this sketchy one
        self.size = size

        self.setGeometry(0, 0, size, size)
        self.setMinimumWidth(size)
        self.setMinimumHeight(size)

        self.compassImage.setTargetWidth(size * 1)
        self.arrowImage.setTargetWidth(size * 1)

    def setCompassColor(self, colorString):
        [r, g, b] = get_rgb_from_string(colorString)
        self.compassImage.setSingleColor(r, g, b)
