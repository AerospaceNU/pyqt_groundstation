"""
Widget for buttons
"""

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QComboBox, QGridLayout, QPushButton, QSizePolicy, QWidget

from src.Widgets import custom_q_widget_base


class ButtonPanel(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, widget: QWidget = None):
        super().__init__(widget)
        self.videoSwitcher = QComboBox()
        self.resetGraphButton = QPushButton()
        self.clearMapButton = QPushButton()
        self.resetDatumButton = QPushButton()
        self.resetOriginButton = QPushButton()

        self.menuItems = []
        self.acousticMode = 2
        self.strobeMode = 3
        self.isBagging = False
        self.initialized = False

        layout = QGridLayout()
        layout.addWidget(self.videoSwitcher, 1, 1)
        layout.addWidget(self.resetGraphButton, 2, 1)
        layout.addWidget(self.clearMapButton, 3, 1)
        layout.addWidget(self.resetDatumButton, 4, 1)
        layout.addWidget(self.resetOriginButton, 5, 1)
        layout.setContentsMargins(3, 5, 3, 5)
        self.setLayout(layout)

        font = QFont("Monospace", 8)
        self.videoSwitcher.setFont(font)
        self.resetGraphButton.setFont(font)
        self.clearMapButton.setFont(font)
        self.resetDatumButton.setFont(font)
        self.resetOriginButton.setFont(font)

        self.resetGraphButton.setText("Clear Graph")
        self.setVideoOptions(["No Video"])
        self.clearMapButton.setText("Clear Map")
        self.resetDatumButton.setText("Reset Datum")
        self.resetOriginButton.setText("Reset Origin")

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def setVideoOptions(self, items):
        if items != self.menuItems:
            self.videoSwitcher.clear()
            self.videoSwitcher.addItems(["Map"])
            self.videoSwitcher.addItems(items)
            self.menuItems = items

    def getSelectedVideo(self):
        return self.videoSwitcher.currentText()

    def updateInFocus(self):
        if "camera" in self.vehicleData:
            cameras = list(self.vehicleData["camera"])
            self.setVideoOptions(cameras)

    def customUpdateAfterThemeSet(self):
        font = QFont("Monospace", 8)
        self.videoSwitcher.setFont(font)

        for widget in [self.resetGraphButton, self.clearMapButton, self.resetDatumButton, self.resetOriginButton]:
            widget.setStyleSheet("QPushButton {font: 8pt Arial; margin:-1px; padding-left: 3px; padding-right: 3px; padding-top: 4px; padding-bottom: 4px;}")
