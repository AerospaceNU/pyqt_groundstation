"""
Attitude Display
"""

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt5.QtGui import QFont

from Widgets.QWidget_Parts import AttitudeDisplayWidget
from Widgets.QWidget_Parts import AltitudeSpeedIndicatorWidget
from Widgets.QWidget_Parts import VSpeedIndicatorWidget
from Widgets.QWidget_Parts import CompassDisplayWidget

from Widgets import CustomQWidgetBase

from data_helpers import getValueFromDictionary, roundToString


class FlightDisplay(CustomQWidgetBase.CustomQWidgetBase):
    def __init__(self, widget: QWidget = None):
        super().__init__(widget)

        self.scale = 200

        self.SpeedTextBox = QLabel()
        self.VSpeedTextBox = QLabel()
        self.AltitudeTextBox = QLabel()
        self.TerrainTextBox = QLabel()

        self.StateTextBox = QLabel()
        self.SetpointTextBox = QLabel()

        self.useAltVSpeedWidget = True
        self.altScale = 1
        self.vSpeedScale = 1
        self.terrainAltScale = 1

        self.pitchSource = "pitch"
        self.rollSource = "roll"
        self.yawSource = "yaw"
        self.altSource = "depth"
        self.speedSource = "groundSpeed"
        self.vSpeedSource = "verticalSpeed"
        self.terrainAltSource = "terrainAlt"

        self.HUDWidget = AttitudeDisplayWidget.AttitudeDisplayWidget()
        self.CompassWidget = CompassDisplayWidget.CompassDisplayWidget()
        self.AltitudeWidget = AltitudeSpeedIndicatorWidget.AltitudeSpeedIndicatorWidget(onScreenSpacingScale=5)
        self.SpeedWidget = AltitudeSpeedIndicatorWidget.AltitudeSpeedIndicatorWidget(leftOriented=False, onScreenSpacingScale=5)
        self.TerrainAltWidget = AltitudeSpeedIndicatorWidget.AltitudeSpeedIndicatorWidget(onScreenSpacingScale=self.terrainAltScale)

        if self.useAltVSpeedWidget:
            self.VSpeedWidget = VSpeedIndicatorWidget.VSpeedIndicatorWidget(maxSpeed=self.vSpeedScale)
        else:
            self.VSpeedWidget = AltitudeSpeedIndicatorWidget.AltitudeSpeedIndicatorWidget(onScreenSpacingScale=self.vSpeedScale)

        layout = QGridLayout()
        layout.addWidget(self.SpeedWidget, 1, 1)
        layout.addWidget(self.HUDWidget, 1, 2)
        layout.addWidget(self.AltitudeWidget, 1, 3)
        layout.addWidget(self.VSpeedWidget, 1, 4)
        layout.addWidget(self.CompassWidget, 3, 2)
        layout.addWidget(self.TerrainAltWidget, 1, 0)
        layout.addWidget(self.TerrainTextBox, 2, 0)

        layout.addWidget(self.SpeedTextBox, 2, 1)
        layout.addWidget(self.VSpeedTextBox, 2, 4)
        layout.addWidget(self.AltitudeTextBox, 2, 3)

        layout.addWidget(self.StateTextBox, 3, 0, 1, 2)
        layout.addWidget(self.SetpointTextBox, 3, 3, 1, 2)

        self.setLayout(layout)

        self.SpeedTextBox.setAlignment(QtCore.Qt.AlignCenter)
        self.AltitudeTextBox.setAlignment(QtCore.Qt.AlignCenter)
        self.VSpeedTextBox.setAlignment(QtCore.Qt.AlignCenter)
        self.TerrainTextBox.setAlignment(QtCore.Qt.AlignCenter)
        self.StateTextBox.setAlignment(QtCore.Qt.AlignCenter)
        self.SetpointTextBox.setAlignment(QtCore.Qt.AlignCenter)

        self.SpeedTextBox.setText("GS")
        self.VSpeedTextBox.setText("VS")
        self.AltitudeTextBox.setText("DEPTH")
        self.TerrainTextBox.setText("ALT")

        self.HUDWidget.setSize(self.scale)
        self.CompassWidget.setSize(self.scale)
        self.AltitudeWidget.setSize(self.scale)
        self.SpeedWidget.setSize(self.scale)
        self.VSpeedWidget.setSize(self.scale)
        self.TerrainAltWidget.setSize(self.scale)

        self.StateTextBox.setFont(QFont("Monospace", 10))
        self.SetpointTextBox.setFont(QFont("Monospace", 10))

        self.setMaximumHeight(self.scale * 2 + 40)
        self.setMaximumWidth(int(self.scale * 2 + 40))

    def updateData(self, vehicleData):
        roll = float(getValueFromDictionary(vehicleData, self.rollSource, 0))
        pitch = float(getValueFromDictionary(vehicleData, self.pitchSource, 0))
        yaw = float(getValueFromDictionary(vehicleData, self.yawSource, 0))
        altitude = float(getValueFromDictionary(vehicleData, self.altSource, 0))
        groundSpeed = float(getValueFromDictionary(vehicleData, self.speedSource, 0))
        vSpeed = float(getValueFromDictionary(vehicleData, self.vSpeedSource, 0))
        terrainAlt = float(getValueFromDictionary(vehicleData, self.terrainAltSource, 0))
        rollSetpoint = float(getValueFromDictionary(vehicleData, "roll_setpoint", 0))
        pitchSetpoint = float(getValueFromDictionary(vehicleData, "pitch_setpoint", 0))
        yawSetpoint = float(getValueFromDictionary(vehicleData, "yaw_setpoint", 0))
        depthSetpoint = float(getValueFromDictionary(vehicleData, "depth_setpoint", 0))
        altSetpoint = float(getValueFromDictionary(vehicleData, "alt_setpoint", 0))
        xPos = float(getValueFromDictionary(vehicleData, "x_position_global", 0))
        yPos = float(getValueFromDictionary(vehicleData, "y_position_global", 0))
        surge_power = float(getValueFromDictionary(vehicleData, "surge_power", 0))

        self.HUDWidget.setRollPitch(roll, pitch)
        self.CompassWidget.setYaw(yaw)
        self.AltitudeWidget.setValue(altitude)
        self.SpeedWidget.setValue(groundSpeed)
        self.VSpeedWidget.setValue(vSpeed)
        self.TerrainAltWidget.setValue(terrainAlt)

        stateText = "Positions:\n"
        stateText += "{0:<7s}{1:>5d}\n".format("roll:", int(roll))
        stateText += "{0:<7s}{1:>5d}\n".format("pitch:", int(pitch))
        stateText += "{0:<7s}{1:>5d}\n".format("yaw:", int(yaw))
        stateText += "{0:<7s}{1:>5s}\n".format("depth:", roundToString(altitude, 5))
        stateText += "{0:<7s}{1:>5s}\n".format("x (e):", roundToString(xPos, 5))
        stateText += "{0:<7s}{1:>5s}\n".format("y (n):", roundToString(yPos, 5))
        self.StateTextBox.setText(stateText)

        setpointText = "Setpoints:\n"
        setpointText += "{0:<7s}{1:>5d}\n".format("roll:", int(rollSetpoint))
        setpointText += "{0:<7s}{1:>5d}\n".format("pitch:", int(pitchSetpoint))
        setpointText += "{0:<7s}{1:>5d}\n".format("yaw:", int(yawSetpoint))
        setpointText += "{0:<7s}{1:>5s}\n".format("depth:", roundToString(depthSetpoint, 5))
        setpointText += "{0:<7s}{1:>5s}\n".format("alt:", roundToString(altSetpoint, 5))
        setpointText += 'Power:\n'
        setpointText += "{0:<7s}{1:>5s}\n".format("surge:", roundToString(surge_power, 5))
        self.SetpointTextBox.setText(setpointText)

        self.update()

    def setWidgetColors(self, widgetBackgroundString, textString, headerTextString, borderString):
        self.SpeedTextBox.setStyleSheet(textString)
        self.VSpeedTextBox.setStyleSheet(textString)
        self.AltitudeTextBox.setStyleSheet(textString)
        self.TerrainTextBox.setStyleSheet(textString)
        self.StateTextBox.setStyleSheet(textString)
        self.SetpointTextBox.setStyleSheet(textString)

        self.CompassWidget.setCompassColor(textString)

        self.setStyleSheet("QWidget#" + self.objectName() + "{" + "{0}{1}{2}{3}".format(widgetBackgroundString, textString, headerTextString, borderString) + "}")
