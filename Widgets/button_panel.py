"""
Widget for buttons
"""

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QComboBox, QSizePolicy, QLabel

from Widgets import custom_q_widget_base


class ButtonPanel(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, widget: QWidget = None):
        super().__init__(widget)
        self.videoSwitcher = QComboBox()
        self.resetGraphButton = QPushButton()
        self.clearMapButton = QPushButton()
        self.resetDatumButton = QPushButton()

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
        self.setLayout(layout)

        font = QFont("Monospace", 8)
        self.videoSwitcher.setFont(font)
        self.resetGraphButton.setFont(font)
        self.clearMapButton.setFont(font)
        self.resetDatumButton.setFont(font)

        self.resetGraphButton.setText("Clear Graph")
        self.setVideoOptions(["No Video"])
        self.clearMapButton.setText("Clear Map")
        self.resetDatumButton.setText("Reset Datum")

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def setVideoOptions(self, items):
        if items != self.menuItems:
            self.videoSwitcher.clear()
            self.videoSwitcher.addItems(["Map"])
            self.videoSwitcher.addItems(items)
            self.menuItems = items

    def getSelectedVideo(self):
        return self.videoSwitcher.currentText()

    def updateData(self, vehicle_data, updated_data):
        if "camera" in vehicle_data:
            cameras = list(vehicle_data["camera"])
            self.setVideoOptions(cameras)

    def setWidgetColors(self, widget_background_string, text_string, header_text_string, border_string):
        string = "{0}{1}{2}{3}".format(widget_background_string, text_string, header_text_string, border_string)
        self.setStyleSheet("QWidget#" + self.objectName() + "{" + string + "}")

        self.videoSwitcher.setStyleSheet(widget_background_string + text_string)
        self.resetGraphButton.setStyleSheet(widget_background_string + text_string)
        self.clearMapButton.setStyleSheet(widget_background_string + text_string)
        self.resetDatumButton.setStyleSheet(widget_background_string + text_string)
