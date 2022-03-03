"""
Custom base QWidget

Currently only used for setting colors properly
"""
import copy

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QWidget, QMenu
from PyQt5.QtGui import QMouseEvent

from data_helpers import make_stylesheet_string, get_rgb_from_string, clamp, get_value_from_dictionary, check_type


class SourceKeyData(object):
    """Data structure to hold info about a source key thingy"""

    def __init__(self, key_name, value_type, default_value):
        self.key_name = key_name
        self.value_type = value_type
        self.default_value = default_value


class CustomQWidgetBase(QWidget):
    def __init__(self, widget: QWidget = None):
        super().__init__(widget)

        self.isInLayout = widget is None

        self.isClicked = False
        self.draggable = True
        self.activeOffset = [0, 0]

        self.borderColor = [0, 0, 0]
        self.backgroundColor = [0, 0, 0]
        self.textColor = [0, 0, 0]
        self.callbackEvents = []
        self.tabName = ""

        self.vehicleData = {}
        self.sourceList = {}

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.rightClickMenu)

    def setTheme(self, widgetBackground, text, headerText, border):
        """I implemented my own theme code instead of using the QT stuff, because this does what I want"""
        widget_background_string = make_stylesheet_string("background", widgetBackground)
        text_string = make_stylesheet_string("color", text)
        header_text_string = make_stylesheet_string("color", headerText)
        border_string = "border: {0}px solid {1};".format(1, border)

        self.borderColor = get_rgb_from_string(border)
        self.backgroundColor = get_rgb_from_string(widgetBackground)
        self.textColor = get_rgb_from_string(text)
        self.setWidgetColors(widget_background_string, text_string, header_text_string, border_string)

    def rightClickMenu(self, e: QPoint):
        menu = QMenu()

        if not self.isInLayout:
            if self.draggable:
                menu.addAction("Disable dragging", lambda draggable=False: self.setDraggable(draggable))
            else:
                menu.addAction("Enable dragging", lambda draggable=True: self.setDraggable(draggable))

            menu.addSeparator()
            menu.addAction("Delete", self.hide)
            menu.addSeparator()

        for source in self.sourceList:
            submenu = menu.addMenu(source)
            available_sources = self.getAvailableSourceOptions(source)

            for option in available_sources:
                submenu.addAction(option, lambda a=source, b=option: self.updateDictKeyTarget(a, b))

        menu.addSeparator()
        self.addCustomMenuItems(menu)
        menu.exec_(self.mapToGlobal(e))

    def addCustomMenuItems(self, menu: QMenu):
        pass

    def requestCallback(self, callback_name, callback_data):
        self.callbackEvents.append([callback_name, callback_data])

    def setDraggable(self, draggable):
        if not self.isInLayout:
            self.draggable = draggable

    def setWidgetColors(self, widget_background_string, text_string, header_text_string, border_string):
        """Overwrite this for each widget"""
        self.setStyleSheet("{0}{1}{2}{3}".format(widget_background_string, text_string, header_text_string, border_string))

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        """Draw border around widget"""
        painter = QPainter(self)  # Grey background
        painter.setPen(QColor(self.borderColor[0], self.borderColor[1], self.borderColor[2]))
        painter.setBrush(QColor(self.backgroundColor[0], self.backgroundColor[1], self.backgroundColor[2]))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

    def coreUpdate(self):
        if not self.isInLayout:
            self.adjustSize()

    def setVehicleData(self, vehicle_data):
        """Called by the tab every loop.  DO NOT OVERRIDE"""
        self.vehicleData = vehicle_data
        self.updateData(vehicle_data)

    def updateData(self, vehicle_data):
        """Called every loop with new vehicle database dictionary"""
        pass

    def updateConsole(self, data):
        pass

    def getCallbackEvents(self):
        """Returns a list of callbacks to be run in the main thread"""
        temp = copy.deepcopy(self.callbackEvents)
        self.callbackEvents = []
        return temp

    def mousePressEvent(self, e: QMouseEvent):
        """Determines if we clicked on a widget"""
        self.isClicked = True
        self.activeOffset = [float(e.screenPos().x()) - self.pos().x(), float(e.screenPos().y()) - self.pos().y()]

    def mouseMoveEvent(self, e: QMouseEvent):
        """Moves the active widget to the position of the mouse if we are currently clicked"""
        if not self.isInLayout and self.isClicked and self.draggable:
            x = clamp(e.screenPos().x() - self.activeOffset[0], 0, self.parent().width() - self.width())
            y = clamp(e.screenPos().y() - self.activeOffset[1], 0, self.parent().height() - self.height())
            self.move(x, y)

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.isClicked = False

    def addSourceKey(self, internal_id: str, value_type, default_key: str, default_value=None):
        self.sourceList[internal_id] = SourceKeyData(default_key, value_type, default_value)

    def getDictValueUsingSourceKey(self, internal_key_id):
        dictionary_key = self.sourceList[internal_key_id].key_name
        default_value = self.sourceList[internal_key_id].default_value
        value_type = self.sourceList[internal_key_id].value_type

        return_value = get_value_from_dictionary(self.vehicleData, dictionary_key, default_value)
        try:
            return value_type(return_value)
        except TypeError:
            return default_value

    def updateDictKeyTarget(self, internal_key_id, new_key):
        self.sourceList[internal_key_id].key_name = new_key

    def getAvailableSourceOptions(self, source):
        value_type = self.sourceList[source].value_type
        option_list = []

        for key in self.vehicleData:
            if check_type(self.vehicleData[key], value_type):
                option_list.append(key)

        return option_list
