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
        self.accelerationScale = 10

        self.addSourceKey("pitch", float, Constants.pitch_position_key, default_value=0, hide_drop_down=True)
        self.addSourceKey("roll", float, Constants.roll_position_key, default_value=0, hide_drop_down=True)
        self.addSourceKey("yaw", float, Constants.yaw_position_key, default_value=0, hide_drop_down=True)
        self.addSourceKey("altitude", float, Constants.altitude_key, default_value=0, hide_drop_down=True)
        self.addSourceKey("speed", float, Constants.ground_speed_key, default_value=0, hide_drop_down=True)
        self.addSourceKey("vspeed", float, Constants.vertical_speed_key, default_value=0, hide_drop_down=True)
        self.addSourceKey("accel", float, Constants.acceleration_key, default_value=0, hide_drop_down=True)

        self.SpeedTextBox = QLabel()
        self.VSpeedTextBox = QLabel()
        self.AltitudeTextBox = QLabel()
        self.TerrainTextBox = QLabel()

        self.HUDWidget = attitude_display_widget.AttitudeDisplayWidget()
        self.AltitudeWidget = altitude_speed_indicator_widget.AltitudeSpeedIndicatorWidget(text_spacing=10, pixels_per_line=20, intermediate_lines=0)
        self.SpeedWidget = altitude_speed_indicator_widget.AltitudeSpeedIndicatorWidget(left_oriented=False, text_spacing=1, pixels_per_line=30, intermediate_lines=2)
        self.AccelerationWidget = v_speed_indicator_widget.VSpeedIndicatorWidget(maxSpeed=self.accelerationScale, leftOriented=False)
        self.VSpeedWidget = altitude_speed_indicator_widget.AltitudeSpeedIndicatorWidget(text_spacing=10, pixels_per_line=20, intermediate_lines=0)

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

    def updateInFocus(self):
        roll = self.getDictValueUsingSourceKey("roll")
        pitch = self.getDictValueUsingSourceKey("pitch")
        yaw = self.getDictValueUsingSourceKey("yaw")
        altitude = self.getDictValueUsingSourceKey("altitude")
        ground_speed = self.getDictValueUsingSourceKey("speed")
        v_speed = self.getDictValueUsingSourceKey("vspeed")
        acceleration = self.getDictValueUsingSourceKey("accel") / 9.8  # m/s^2 to g

        self.HUDWidget.setRollPitch(roll, pitch)
        self.AltitudeWidget.setValue(altitude)
        self.SpeedWidget.setValue(ground_speed)
        self.VSpeedWidget.setValue(v_speed)
        self.AccelerationWidget.setValue(acceleration)

        if self.compass_and_text:
            self.CompassWidget.setYaw(yaw)

            state_text = "Positions:\n"
            state_text += "{0:<7s}{1:>5d}\n".format("roll:", int(roll))
            state_text += "{0:<7s}{1:>5d}\n".format("pitch:", int(pitch))
            state_text += "{0:<7s}{1:>5d}\n".format("yaw:", int(yaw))
            state_text += "{0:<7s}{1:>5s}\n".format("depth:", round_to_string(altitude, 5))
            # state_text += "{0:<7s}{1:>5s}\n".format("x (e):", round_to_string(xPos, 5))
            # state_text += "{0:<7s}{1:>5s}\n".format("y (n):", round_to_string(yPos, 5))
            self.StateTextBox.setText(state_text)

            setpoint_text = "Setpoints:\n"
            # setpoint_text += "{0:<7s}{1:>5d}\n".format("roll:", int(rollSetpoint))
            # setpoint_text += "{0:<7s}{1:>5d}\n".format("pitch:", int(pitchSetpoint))
            # setpoint_text += "{0:<7s}{1:>5d}\n".format("yaw:", int(yawSetpoint))
            # setpoint_text += "{0:<7s}{1:>5s}\n".format("depth:", round_to_string(depthSetpoint, 5))
            # setpoint_text += "{0:<7s}{1:>5s}\n".format("alt:", round_to_string(altSetpoint, 5))
            setpoint_text += 'Power:\n'
            # setpoint_text += "{0:<7s}{1:>5s}\n".format("surge:", round_to_string(surge_power, 5))
            self.SetpointTextBox.setText(setpoint_text)

        self.update()
        self.adjustSize()

    def setWidgetColors(self, widget_background_string, text_string, header_text_string, border_string):
        self.SpeedTextBox.setStyleSheet(text_string)
        self.VSpeedTextBox.setStyleSheet(text_string)
        self.AltitudeTextBox.setStyleSheet(text_string)
        self.TerrainTextBox.setStyleSheet(text_string)
        self.HUDWidget.setStyleSheet(text_string)

        if self.compass_and_text:
            self.CompassWidget.setCompassColor(text_string)
            self.StateTextBox.setStyleSheet(text_string)
            self.SetpointTextBox.setStyleSheet(text_string)

        self.setStyleSheet("QWidget#" + self.objectName() + "{" + "{0}{1}{2}{3}".format(widget_background_string, text_string, header_text_string, border_string) + "}")
