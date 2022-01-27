"""
Specific widget to display ROV status
"""

import time

from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QSizePolicy

from Widgets import CustomQWidgetBase

from Widgets.QWidget_Parts import SimpleBarGraphWidget, CircleBarGraphWidget

from data_helpers import getValueFromDictionary


class VehicleStatusWidget(CustomQWidgetBase.CustomQWidgetBase):
    def __init__(self, widget: QWidget = None):
        super().__init__(widget)
        self.statusBox = QLabel()
        self.armingBox = QLabel()
        self.modeBox = QLabel()
        self.timeBox = QLabel()
        self.runtimeBox = QLabel()
        self.acousticBox = QLabel()
        self.depthModeBox = QLabel()

        self.Percent = CircleBarGraphWidget.CircleBarGraphWidget(title="Percent", minValue=0, maxValue=1)
        self.Voltage = SimpleBarGraphWidget.SimpleBarGraphWidget(title="Voltage", minValue=13, maxValue=16.4)
        self.Current = SimpleBarGraphWidget.SimpleBarGraphWidget(title="Current", minValue=0, maxValue=30)
        self.CPUGraph = SimpleBarGraphWidget.SimpleBarGraphWidget(title="CPU", minValue=0, maxValue=100)
        self.RAMGraph = SimpleBarGraphWidget.SimpleBarGraphWidget(title="RAM", minValue=0, maxValue=100)
        self.DISKGraph = SimpleBarGraphWidget.SimpleBarGraphWidget(title="Disk", minValue=0, maxValue=100)

        layout = QGridLayout()
        layout.addWidget(self.statusBox, 1, 1, 4, 1)
        layout.addWidget(self.armingBox, 1, 2, 4, 1)
        layout.addWidget(self.modeBox, 1, 3, 4, 1)
        layout.addWidget(self.timeBox, 1, 4)
        layout.addWidget(self.runtimeBox, 2, 4)
        layout.addWidget(self.acousticBox, 3, 4)
        layout.addWidget(self.depthModeBox, 4, 4)
        layout.addWidget(self.Percent, 1, 5, 4, 1)
        layout.addWidget(self.Voltage, 1, 6, 4, 1)
        layout.addWidget(self.Current, 1, 7, 4, 1)
        layout.addWidget(self.CPUGraph, 1, 8, 4, 1)
        layout.addWidget(self.RAMGraph, 1, 9, 4, 1)
        layout.addWidget(self.DISKGraph, 1, 10, 4, 1)
        self.setLayout(layout)

        self.widgetSize = 20
        self.title = None
        self.font = None
        self.fontSize = None

        self.statusSource = "status"
        self.armedSource = "armed"
        self.allowedToArmSource = "allowedToArm"
        self.modeSource = "driveMode"
        self.runtimeSource = "runtime"
        self.vehicleTimeSource = "system_time"
        self.depthModeSource = "depth_control_mode"

        self.statusBox.setFont(QFont("Monospace", self.widgetSize))
        self.statusBox.setAlignment(QtCore.Qt.AlignCenter)
        self.statusBox.setMinimumWidth(self.widgetSize * 8)

        self.armingBox.setFont(QFont("Monospace", self.widgetSize))
        self.armingBox.setAlignment(QtCore.Qt.AlignCenter)
        self.armingBox.setMinimumWidth(self.widgetSize * 13)

        self.modeBox.setFont(QFont("Monospace", self.widgetSize))
        self.modeBox.setAlignment(QtCore.Qt.AlignCenter)
        self.modeBox.setMinimumWidth(self.widgetSize * 13)

        for box in [self.timeBox, self.acousticBox, self.runtimeBox, self.depthModeBox]:
            box.setFont(QFont("Monospace", self.widgetSize * 0.4))

    def updateData(self, vehicleData):
        if "status" not in vehicleData:
            self.setMinimumSize(5, 5)
            return
        data = vehicleData["status"]

        faultStatus = int(float(getValueFromDictionary(data, self.statusSource, 3)))
        canArm = int(float(getValueFromDictionary(data, self.allowedToArmSource, True)))
        armed = int(float(getValueFromDictionary(data, self.armedSource, True)))
        mode = str(getValueFromDictionary(data, self.modeSource, "Unknown"))
        runtime = getValueFromDictionary(data, self.runtimeSource, "0")
        systemTime = getValueFromDictionary(data, self.vehicleTimeSource, "0")
        acousticStatus = getValueFromDictionary(data, "acoustic_enable", "unknown")
        depth_mode = getValueFromDictionary(data, self.depthModeSource, "unknown")

        if str(acousticStatus).lower() == "true":  # I'm not sure if its a string or bool
            acousticStatus = "Enabled"
        elif str(acousticStatus).lower() == "false":
            acousticStatus = "Disabled"

        percent = getValueFromDictionary(data, "battery_percent", -1)
        voltage = getValueFromDictionary(data, "battery_voltage", -1)
        current = getValueFromDictionary(data, "battery_current", -1)
        cpu = getValueFromDictionary(data, "cpu_usage", -1)
        ram = getValueFromDictionary(data, "ram_usage", -1)
        disk = getValueFromDictionary(data, "disk_usage", -1)

        if faultStatus == 2:
            self.statusBox.setStyleSheet("color: red")
            self.statusBox.setText("Faulted")
        elif faultStatus == 1:
            self.statusBox.setStyleSheet("color: yellow")
            self.statusBox.setText("Warning")
        elif faultStatus == 0:
            self.statusBox.setStyleSheet("color: green")
            self.statusBox.setText("OK")
        else:
            self.statusBox.setStyleSheet("color: blue")
            self.statusBox.setText("Unknown")

        if not canArm:
            self.armingBox.setText("Arming Disabled")
            self.armingBox.setStyleSheet("color: red")
        else:
            self.armingBox.setStyleSheet("color: green")
            if armed:
                self.armingBox.setText("Armed")
            else:
                self.armingBox.setText("Disarmed")

        self.modeBox.setText(mode)
        self.timeBox.setText(systemTime)
        self.runtimeBox.setText("Run Time: {}".format(runtime))
        self.acousticBox.setText("Acoustics: {}".format(acousticStatus))
        self.depthModeBox.setText("Depth mode: {}".format(depth_mode))

        self.statusBox.adjustSize()
        self.armingBox.adjustSize()
        self.modeBox.adjustSize()
        self.depthModeBox.adjustSize()
        self.setMaximumHeight(self.modeBox.height() * 2 + 20)

        self.Voltage.fixWidth(0.7)
        self.Current.fixWidth(0.7)
        self.Percent.setSize(self.Current.height())
        self.CPUGraph.fixWidth(0.7)
        self.RAMGraph.fixWidth(0.7)
        self.DISKGraph.fixWidth(0.7)

        self.Percent.setValue(percent)
        self.Voltage.setValue(voltage)
        self.Current.setValue(current)
        self.CPUGraph.setValue(cpu)
        self.RAMGraph.setValue(ram)
        self.DISKGraph.setValue(disk)

    def setWidgetColors(self, widgetBackgroundString, textString, headerTextString, borderString):
        self.modeBox.setStyleSheet(textString)
        self.timeBox.setStyleSheet(textString)
        self.runtimeBox.setStyleSheet(textString)
        self.acousticBox.setStyleSheet(textString)
        self.depthModeBox.setStyleSheet(textString)

        self.Percent.setTextColor(textString)
        self.Voltage.setTextColor(textString)
        self.Current.setTextColor(textString)
        self.CPUGraph.setTextColor(textString)
        self.RAMGraph.setTextColor(textString)
        self.DISKGraph.setTextColor(textString)
