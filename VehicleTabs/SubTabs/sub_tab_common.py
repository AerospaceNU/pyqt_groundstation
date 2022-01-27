"""
Code to define widget layout to drive warpauv
"""

from PyQt5.QtWidgets import QWidget


class SubTab(object):
    def __init__(self):
        self.mainWidget = QWidget()

        self.canAddWidgets = False

        self.widgetList = []

    def getMainWidget(self):
        return self.mainWidget

    def addWidget(self, widget: QWidget):
        self.widgetList.append(widget)
        return widget

    def getWidgetList(self):
        return self.widgetList

    def update(self):
        pass
