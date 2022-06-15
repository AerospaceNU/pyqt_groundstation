"""
Code used in all vehicle tabs
"""
from typing import List
from PyQt5 import QtGui

from src.Widgets.custom_q_widget_base import CustomQWidgetBase


class TabCommon(CustomQWidgetBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.vehicleName = ""
        self.isActiveTab = False

        self.widgetsCreated = 0
        self.widgetList: List[CustomQWidgetBase] = []

    def rightClickMenu(self, e):
        return

    def updateVehicleData(self, data, console_data, updated_data):
        """The update function that should not be overridden"""
        if isinstance(data, dict):
            vehicle_data = data
        else:
            vehicle_data = {}

        if not isinstance(updated_data, dict):
            updated_data = {}

        callbacks = []

        for widget in self.widgetList:
            callbacks += widget.updateVehicleData(vehicle_data, console_data, updated_data)

        self.customUpdateVehicleData(data)

        self.update()

        return callbacks

    def setRecordedData(self, recorded_data):
        self.recordedData = recorded_data
        for widget in self.widgetList:
            widget.setRecordedData(recorded_data)

    def customUpdateVehicleData(self, data):
        """The update function that should be overridden"""
        pass

    def addWidget(self, widget: CustomQWidgetBase, widget_name=None) -> CustomQWidgetBase:
        if widget_name is None:
            widget_name = str(type(widget)).split(".")[-1][:-2]

        self.widgetList.append(widget)
        widget.show()
        self.widgetList[-1].setObjectName("{0}_{1}_{2}".format(self.vehicleName, widget_name, self.widgetsCreated))
        self.widgetList[-1].tabName = self.vehicleName  # Kind of a hack
        self.widgetsCreated += 1
        return widget

    def updateAfterThemeSet(self):
        for widget in self.widgetList:
            widget.updateAfterThemeSet()

        self.setStyleSheet("QWidget#" + self.objectName() + " {border: 0}")
