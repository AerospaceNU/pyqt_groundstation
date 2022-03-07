"""
Code used in all vehicle tabs
"""

from PyQt5.QtWidgets import QWidget

from Widgets import custom_q_widget_base
from data_helpers import make_stylesheet_string, get_well_formatted_rgb_string


class TabCommon(QWidget):
    def __init__(self, vehicleName: str):
        super().__init__()
        self.setObjectName("tab_{}".format(vehicleName))

        self.vehicleName = vehicleName
        self.widgetsCreated = 0

        self.widgetList = []

        self.colors = []

    def updateVehicleData(self, data, console_data, updated_data):
        """The update function that should not be overridden"""
        if isinstance(data, dict):
            vehicleData = data
        else:
            vehicleData = {}

        if not isinstance(updated_data, dict):
            updated_data = {}

        callbacks = []

        for widget in self.widgetList:
            widget.setVehicleData(vehicleData, updated_data)
            widget.updateConsole(console_data)
            widget.coreUpdate()
            callbacks += widget.getCallbackEvents()

        self.update()

        self.customUpdate(data)
        return callbacks

    def customUpdate(self, data):
        """The update function that should be overridden"""
        pass

    def addWidget(self, widget: custom_q_widget_base, widgetName="_") -> custom_q_widget_base.CustomQWidgetBase:
        self.widgetList.append(widget)
        widget.show()
        self.widgetList[-1].setObjectName("{0}_{1}_{2}".format(self.vehicleName, widgetName, self.widgetsCreated))
        self.widgetList[-1].tabName = self.vehicleName  # Kind of a hack
        self.widgetsCreated += 1
        return widget

    def setTheme(self, background, widgetBackground, text, headerText, border):
        background_string = make_stylesheet_string("background", background)
        color_string = make_stylesheet_string("color", text)
        border_string = "border: 1px solid " + get_well_formatted_rgb_string("rgb[10,10,10]") + ";"
        self.setStyleSheet("QWidget#" + self.objectName() + "{" + background_string + color_string + border_string + "}")

        for widget in self.widgetList:
            widget.setTheme(widgetBackground, text, headerText, border)

        self.colors = [background, widgetBackground, text, headerText, border]

    def updateTheme(self):
        self.setTheme(self.colors[0], self.colors[1], self.colors[2], self.colors[3], self.colors[4])
