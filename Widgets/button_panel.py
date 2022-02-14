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
        self.calibratePressure = QPushButton()
        self.acousticSwitcherTextBox = QLabel()
        self.acousticSwitcherButton = QPushButton()
        self.bagControlTextBox = QLabel()
        self.bagControlButton = QPushButton()
        self.clearMapButton = QPushButton()
        self.resetDatumButton = QPushButton()

        self.menuItems = []
        self.acousticMode = 2
        self.strobeMode = 3
        self.isBagging = False
        self.initialized = False

        layout = QGridLayout()
        layout.addWidget(self.videoSwitcher, 1, 1)
        # layout.addWidget(self.calibratePressure, 2, 1)
        # layout.addWidget(self.acousticSwitcherTextBox, 3, 1)
        # layout.addWidget(self.acousticSwitcherButton, 4, 1)
        # layout.addWidget(self.bagControlTextBox, 5, 1)
        # layout.addWidget(self.bagControlButton, 6, 1)
        layout.addWidget(self.clearMapButton, 2, 1)
        layout.addWidget(self.resetDatumButton, 3, 1)
        self.setLayout(layout)

        font = QFont("Monospace", 9)
        self.videoSwitcher.setFont(font)
        self.calibratePressure.setFont(font)
        self.acousticSwitcherTextBox.setFont(font)
        self.acousticSwitcherButton.setFont(font)
        self.bagControlTextBox.setFont(font)
        self.bagControlButton.setFont(font)
        self.clearMapButton.setFont(font)
        self.resetDatumButton.setFont(font)

        self.calibratePressure.setText("MS5837 Cal")
        self.acousticSwitcherTextBox.setText("Acoustics")
        self.bagControlTextBox.setText("Bagging")
        self.setVideoOptions(["No Video"])
        self.clearMapButton.setText("Clear Map")
        self.resetDatumButton.setText("Reset Datum")

        self.acousticSwitcherButton.clicked.connect(self.acousticButtonPress)
        self.calibratePressure.clicked.connect(self.calibrateButtonPress)
        self.bagControlButton.clicked.connect(self.bagButtonPress)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def setVideoOptions(self, items):
        if items != self.menuItems:
            self.videoSwitcher.clear()
            self.videoSwitcher.addItems(["Map"])
            self.videoSwitcher.addItems(items)
            self.menuItems = items

    def getSelectedVideo(self):
        return self.videoSwitcher.currentText()

    def acousticButtonPress(self):
        if self.acousticMode == 2:
            self.acousticMode = 0
        else:
            self.acousticMode += 1

        self.callbackEvents.append(["{}_acoustic_mode_button".format(self.tabName), self.acousticMode])

    def calibrateButtonPress(self):
        self.callbackEvents.append(["{}_pressure_sensor_cal".format(self.tabName), ""])

    def bagButtonPress(self):
        self.isBagging = not self.isBagging
        self.callbackEvents.append(["{}_bagging".format(self.tabName), self.isBagging])

    def updateData(self, vehicleData):
        if "camera" in vehicleData:
            cameras = list(vehicleData["camera"])
            self.setVideoOptions(cameras)

        if self.acousticMode == 0:
            self.acousticSwitcherButton.setText("Disabled")
        elif self.acousticMode == 1:
            self.acousticSwitcherButton.setText("Enabled")
        elif self.acousticMode == 2:
            self.acousticSwitcherButton.setText("Auto")
        else:
            self.acousticMode = 0

        if self.isBagging:
            self.bagControlButton.setText("Enabled")
        else:
            self.bagControlButton.setText("Disabled")

    def setWidgetColors(self, widgetBackgroundString, textString, headerTextString, borderString):
        string = "{0}{1}{2}{3}".format(widgetBackgroundString, textString, headerTextString, borderString)
        self.setStyleSheet("QWidget#" + self.objectName() + "{" + string + "}")

        self.videoSwitcher.setStyleSheet(widgetBackgroundString + textString)
        self.calibratePressure.setStyleSheet(widgetBackgroundString + textString)
        self.acousticSwitcherTextBox.setStyleSheet(widgetBackgroundString + textString)
        self.acousticSwitcherButton.setStyleSheet(widgetBackgroundString + textString)
        self.bagControlTextBox.setStyleSheet(widgetBackgroundString + textString)
        self.bagControlButton.setStyleSheet(widgetBackgroundString + textString)
        self.clearMapButton.setStyleSheet(widgetBackgroundString + textString)
        self.resetDatumButton.setStyleSheet(widgetBackgroundString + textString)
