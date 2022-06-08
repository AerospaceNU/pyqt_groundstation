"""
Code used in all vehicle tabs
"""
from PyQt5 import QtGui

from src.Widgets import custom_q_widget_base


class TabCommon(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.vehicleName = ""
        self.isActiveTab = False

        self.widgetsCreated = 0
        self.widgetList = []

    def rightClickMenu(self, e):
        return

    def updateVehicleData(self, data, console_data, updated_data, recorded_data):
        """The update function that should not be overridden"""
        if isinstance(data, dict):
            vehicle_data = data
        else:
            vehicle_data = {}

        if not isinstance(updated_data, dict):
            updated_data = {}

        callbacks = []

        for widget in self.widgetList:
            callbacks += widget.updateVehicleData(vehicle_data, console_data, updated_data, recorded_data)
            widget.coreUpdate()

        self.customUpdateVehicleData(data)

        self.update()

        return callbacks

    def customUpdateVehicleData(self, data):
        """The update function that should be overridden"""
        pass

    def addWidget(self, widget: custom_q_widget_base.CustomQWidgetBase, widget_name=None) -> custom_q_widget_base.CustomQWidgetBase:
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
