"""
Attitude Display
"""

from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel

from Widgets import custom_q_widget_base
from Widgets.QWidget_Parts import altitude_speed_indicator_widget
from Widgets.QWidget_Parts import attitude_display_widget
from Widgets.QWidget_Parts import compass_display_widget
from Widgets.QWidget_Parts import v_speed_indicator_widget
from data_helpers import get_value_from_dictionary, round_to_string
from constants import Constants


class FlightDisplay(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, widget: QWidget = None, compass_and_text=False):
        super().__init__(widget)

        self.scale = 200
        v_scale_factor = 1
        self.compass_and_text = compass_and_text
        self.useAltVSpeedWidget = False
        self.altScale = 1
        self.vSpeedScale = 1
        self.accelerationScale = 1

        self.pitchSource = "pitch"
        self.rollSource = "roll"
        self.yawSource = "yaw"
        self.altSource = Constants.altitude_key
        self.speedSource = "groundSpeed"
        self.vSpeedSource = Constants.vertical_speed_key
        self.terrainAltSource = "acceleration"

        self.SpeedTextBox = QLabel()
        self.VSpeedTextBox = QLabel()
        self.AltitudeTextBox = QLabel()
        self.TerrainTextBox = QLabel()

        self.HUDWidget = attitude_display_widget.AttitudeDisplayWidget()
        self.AltitudeWidget = altitude_speed_indicator_widget.AltitudeSpeedIndicatorWidget(textSpacing=0.1)
        self.SpeedWidget = altitude_speed_indicator_widget.AltitudeSpeedIndicatorWidget(leftOriented=False, textSpacing=0.1)
        self.AccelerationWidget = v_speed_indicator_widget.VSpeedIndicatorWidget(maxSpeed=self.accelerationScale, leftOriented=False)
        self.VSpeedWidget = altitude_speed_indicator_widget.AltitudeSpeedIndicatorWidget(textSpacing=1)

        layout = QGridLayout()
        layout.addWidget(self.SpeedWidget, 1, 1)
        layout.addWidget(self.HUDWidget, 1, 2)
        layout.addWidget(self.AltitudeWidget, 1, 3)
        layout.addWidget(self.VSpeedWidget, 1, 4)
        layout.addWidget(self.AccelerationWidget, 1, 0)
        layout.addWidget(self.TerrainTextBox, 2, 0)

        layout.addWidget(self.SpeedTextBox, 2, 1)
        layout.addWidget(self.VSpeedTextBox, 2, 4)
        layout.addWidget(self.AltitudeTextBox, 2, 3)

        # Configurations
        if self.compass_and_text:
            self.CompassWidget = compass_display_widget.CompassDisplayWidget()
            self.CompassWidget.setSize(self.scale)
            layout.addWidget(self.CompassWidget, 3, 2)

            self.StateTextBox = QLabel()
            self.StateTextBox.setFont(QFont("Monospace", 10))
            self.StateTextBox.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(self.StateTextBox, 3, 0, 1, 2)

            self.SetpointTextBox = QLabel()
            self.SetpointTextBox.setFont(QFont("Monospace", 10))
            self.SetpointTextBox.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(self.SetpointTextBox, 3, 3, 1, 2)

            v_scale_factor = 2

        self.setLayout(layout)

        self.SpeedTextBox.setAlignment(QtCore.Qt.AlignCenter)
        self.AltitudeTextBox.setAlignment(QtCore.Qt.AlignCenter)
        self.VSpeedTextBox.setAlignment(QtCore.Qt.AlignCenter)
        self.TerrainTextBox.setAlignment(QtCore.Qt.AlignCenter)

        self.SpeedTextBox.setText("GS")
        self.VSpeedTextBox.setText("VS")
        self.AltitudeTextBox.setText("ALT")
        self.TerrainTextBox.setText("A")

        self.HUDWidget.setSize(self.scale)
        self.AltitudeWidget.setSize(self.scale)
        self.SpeedWidget.setSize(self.scale)
        self.VSpeedWidget.setSize(self.scale)
        self.AccelerationWidget.setSize(self.scale)

        self.setMaximumHeight(self.scale * v_scale_factor + 40)
        self.setMaximumWidth(int(self.scale * 2 + 40))

    def updateData(self, vehicleData):
        roll = float(get_value_from_dictionary(vehicleData, self.rollSource, 0))
        pitch = float(get_value_from_dictionary(vehicleData, self.pitchSource, 0))
        yaw = float(get_value_from_dictionary(vehicleData, self.yawSource, 0))
        altitude = float(get_value_from_dictionary(vehicleData, self.altSource, 0))
        groundSpeed = float(get_value_from_dictionary(vehicleData, self.speedSource, 0))
        vSpeed = float(get_value_from_dictionary(vehicleData, self.vSpeedSource, 0))
        terrainAlt = float(get_value_from_dictionary(vehicleData, self.terrainAltSource, 0))
        rollSetpoint = float(get_value_from_dictionary(vehicleData, "roll_setpoint", 0))
        pitchSetpoint = float(get_value_from_dictionary(vehicleData, "pitch_setpoint", 0))
        yawSetpoint = float(get_value_from_dictionary(vehicleData, "yaw_setpoint", 0))
        depthSetpoint = float(get_value_from_dictionary(vehicleData, "depth_setpoint", 0))
        altSetpoint = float(get_value_from_dictionary(vehicleData, "alt_setpoint", 0))
        xPos = float(get_value_from_dictionary(vehicleData, "x_position_global", 0))
        yPos = float(get_value_from_dictionary(vehicleData, "y_position_global", 0))
        surge_power = float(get_value_from_dictionary(vehicleData, "surge_power", 0))

        self.HUDWidget.setRollPitch(roll, pitch)
        self.AltitudeWidget.setValue(altitude)
        self.SpeedWidget.setValue(groundSpeed)
        self.VSpeedWidget.setValue(vSpeed)
        self.AccelerationWidget.setValue(terrainAlt)

        if self.compass_and_text:
            self.CompassWidget.setYaw(yaw)

            stateText = "Positions:\n"
            stateText += "{0:<7s}{1:>5d}\n".format("roll:", int(roll))
            stateText += "{0:<7s}{1:>5d}\n".format("pitch:", int(pitch))
            stateText += "{0:<7s}{1:>5d}\n".format("yaw:", int(yaw))
            stateText += "{0:<7s}{1:>5s}\n".format("depth:", round_to_string(altitude, 5))
            stateText += "{0:<7s}{1:>5s}\n".format("x (e):", round_to_string(xPos, 5))
            stateText += "{0:<7s}{1:>5s}\n".format("y (n):", round_to_string(yPos, 5))
            self.StateTextBox.setText(stateText)

            setpointText = "Setpoints:\n"
            setpointText += "{0:<7s}{1:>5d}\n".format("roll:", int(rollSetpoint))
            setpointText += "{0:<7s}{1:>5d}\n".format("pitch:", int(pitchSetpoint))
            setpointText += "{0:<7s}{1:>5d}\n".format("yaw:", int(yawSetpoint))
            setpointText += "{0:<7s}{1:>5s}\n".format("depth:", round_to_string(depthSetpoint, 5))
            setpointText += "{0:<7s}{1:>5s}\n".format("alt:", round_to_string(altSetpoint, 5))
            setpointText += 'Power:\n'
            setpointText += "{0:<7s}{1:>5s}\n".format("surge:", round_to_string(surge_power, 5))
            self.SetpointTextBox.setText(setpointText)

        self.update()
        self.adjustSize()

    def setWidgetColors(self, widgetBackgroundString, textString, headerTextString, borderString):
        self.SpeedTextBox.setStyleSheet(textString)
        self.VSpeedTextBox.setStyleSheet(textString)
        self.AltitudeTextBox.setStyleSheet(textString)
        self.TerrainTextBox.setStyleSheet(textString)

        if self.compass_and_text:
            self.CompassWidget.setCompassColor(textString)
            self.StateTextBox.setStyleSheet(textString)
            self.SetpointTextBox.setStyleSheet(textString)

        self.setStyleSheet("QWidget#" + self.objectName() + "{" + "{0}{1}{2}{3}".format(widgetBackgroundString, textString, headerTextString, borderString) + "}")
