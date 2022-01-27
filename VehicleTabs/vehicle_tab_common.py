"""
Code used in all vehicle tabs
"""

import inspect
import types

from PyQt5.QtWidgets import QWidget, QGridLayout, QTabWidget

from data_helpers import makeStylesheetString

from Widgets import FlightDisplay
from Widgets import VehicleStatusWidget
from Widgets import VideoWidget
from Widgets import ControlStationStatus
from Widgets import AnnunciatorPanel
from Widgets import ButtonPanel
from Widgets import SimpleConsoleWidget
from Widgets import MapWidget
from Widgets import TextBoxDropDownWidget
from Widgets import Reconfigure

from VehicleTabs.SubTabs.sub_tab_common import SubTab
from VehicleTabs.SubTabs.primary_tab import PrimaryTab
from VehicleTabs.SubTabs.diagnostic_tab import DiagnosticTab


class VehicleTabCommon(object):
    def __init__(self, mainWidget: QWidget, vehicleName: str):
        self.mainWidget = mainWidget
        self.mainWidget.setObjectName("tab_{}".format(vehicleName))
        self.layout = QGridLayout()
        self.mainWidget.setLayout(self.layout)

        self.vehicleName = vehicleName
        self.widgetsCreated = 0

        # Code to do dynamic creation of classes
        self.widgetClasses = {}
        for name, val in globals().items():  # Loop through globals()
            if isinstance(val, types.ModuleType) and "Widgets." in str(val):  # Only look at modules from Widgets
                for item in inspect.getmembers(val):
                    if name in str(item) and "__" not in str(item) and "Placeholder" not in name and 'WidgetClasses.QWidgets' not in str(item) and "Helpers" not in str(item):
                        self.widgetClasses[name] = item[1]

        self.widgetList = []
        self.subTabs = []
        self.subTabObjects = []

        self.hasSubTabs = False

        self.subTabHolder = QTabWidget()
        self.subTabHolder.setObjectName("{}_Tab_Holder".format(vehicleName))
        self.subTabHolder.tabBar().setObjectName("{}_Tab_Bar".format(vehicleName))

        self.colors = []

    def update(self, data, controlStationData, rosConsole):
        """The update function that should not be overridden"""
        if isinstance(data, dict) and self.vehicleName in data:
            vehicleData = data[self.vehicleName]
        else:
            vehicleData = {}

        callbacks = []

        for widget in self.widgetList:
            widget.updateData(vehicleData)
            widget.updateControlStationData(controlStationData)
            widget.updateROSConsole(rosConsole)
            widget.coreUpdate()
            callbacks += widget.getCallbackEvents()

        for subTab in self.subTabObjects:
            subTab.update()

        self.customUpdate(data)
        return callbacks

    def customUpdate(self, data):
        """The update function that should be overridden"""
        pass

    def createWidgetFromName(self, widgetName, parent=None):
        """Will create any widget from its file name!"""
        if widgetName not in self.widgetClasses:
            print("No widget of type {}".format(widgetName))
            return QWidget()  # Kind of a hack
        try:
            widget = self.widgetClasses[widgetName](parent)
            self.addWidget(widget, widgetName)
            return widget
        except all as e:
            print("Dynamically creating {} type widgets is not supported yet".format(widgetName))
            print(e)
            return QWidget()

    def addSubTab(self, name, tabType="empty"):
        if not self.hasSubTabs:
            self.layout.addWidget(self.subTabHolder, 1, 1)
            self.hasSubTabs = True

        if tabType == "empty":
            self.addSubTabObject(SubTab())
            self.subTabObjects[-1].canAddWidgets = True
        elif tabType == "primary":
            self.addSubTabObject(PrimaryTab())
        elif tabType == "diagnostic":
            self.addSubTabObject(DiagnosticTab())
        else:
            print("Can't add tab of name {0} and type {1}: type not supported".format(name, tabType))
            return

        self.subTabs[-1].setObjectName("{0}_{1}_tab".format(self.vehicleName, name))
        self.subTabHolder.addTab(self.subTabs[-1], name)

    def addSubTabObject(self, subTabObject):
        self.subTabObjects.append(subTabObject)
        self.subTabs.append(subTabObject.getMainWidget())

        newWidgets = subTabObject.getWidgetList()
        for widget in newWidgets:
            widget.setObjectName("{0}_{1}".format(self.vehicleName, self.widgetsCreated))
            widget.tabName = self.vehicleName
            self.widgetsCreated += 1
        self.widgetList += newWidgets

    def addWidgetToActiveSubTab(self, widgetName):
        if self.subTabHolder.count() > 0:
            tabIndex = self.subTabHolder.currentIndex()
            if self.subTabObjects[tabIndex].canAddWidgets:
                widget = self.createWidgetFromName(widgetName, self.subTabObjects[tabIndex].getMainWidget())
                widget.show()
        else:
            widget = self.createWidgetFromName(widgetName, parent=self.mainWidget)
            widget.show()
        self.updateTheme()

    def addWidget(self, widget: QWidget, widgetName="_"):
        self.widgetList.append(widget)
        self.widgetList[-1].setObjectName("{0}_{1}_{2}".format(self.vehicleName, widgetName, self.widgetsCreated))
        self.widgetList[-1].tabName = self.vehicleName  # Kind of a hack
        self.widgetsCreated += 1
        return widget

    def setTheme(self, background, widgetBackground, text, headerText, border):
        self.mainWidget.setStyleSheet("QWidget#" + self.mainWidget.objectName() + "{" + background + text + "}")
        self.subTabHolder.setStyleSheet("QWidget#" + self.subTabHolder.objectName() + "{" + makeStylesheetString("background", background) + makeStylesheetString("color", text) + "}")
        self.subTabHolder.tabBar().setStyleSheet("QWidget#" + self.subTabHolder.tabBar().objectName() + "{" + makeStylesheetString("background", background) + makeStylesheetString("color", text) + "}")

        for tab in self.subTabs:
            tab.setStyleSheet("QWidget#" + tab.objectName() + "{background: " + background + "; color: " + text + "}")

        for widget in self.widgetList:
            widget.setTheme(widgetBackground, text, headerText, border)

        self.colors = [background, widgetBackground, text, headerText, border]

    def updateTheme(self):
        self.setTheme(self.colors[0], self.colors[1], self.colors[2], self.colors[3], self.colors[4])
