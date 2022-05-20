"""
Custom base QWidget

Handles everything that is needed to be common between widgets
"""

import copy

from PyQt5 import QtGui
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QColor, QMouseEvent, QPainter
from PyQt5.QtWidgets import QMenu, QWidget

from src.data_helpers import (
    check_type,
    clamp,
    get_rgb_from_string,
    get_value_from_dictionary,
    make_stylesheet_string,
)


class SourceKeyData(object):
    """Data structure to hold info about a source key thingy"""

    def __init__(self, key_name, value_type, default_value, hide_in_drop_down):
        self.key_name = key_name
        self.value_type = value_type
        self.default_value = default_value
        self.hide_in_drop_down = hide_in_drop_down


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
        self.borderColorString = ""
        self.backgroundColorString = ""
        self.textColorString = ""
        self.headerTextColorString = ""

        self.callbackEvents = []
        self.tabName = ""

        self.vehicleData = {}
        self.recordedData = {}
        self.updated_data_dictionary = (
            {}
        )  # Tracks which keys are new since the last GUI loop
        self.sourceDictionary = {}

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.rightClickMenu)

    def setTheme(self, widgetBackground, text, headerText, border):
        """I implemented my own theme code instead of using the QT stuff, because this does what I want"""
        self.backgroundColorString = make_stylesheet_string(
            "background", widgetBackground
        )
        self.textColorString = make_stylesheet_string("color", text)
        self.headerTextColorString = make_stylesheet_string("color", headerText)
        self.borderColorString = "border: {0}px solid {1};".format(1, border)

        self.borderColor = get_rgb_from_string(border)
        self.backgroundColor = get_rgb_from_string(widgetBackground)
        self.textColor = get_rgb_from_string(text)
        self.setWidgetColors(
            self.backgroundColorString,
            self.textColorString,
            self.headerTextColorString,
            self.borderColorString,
        )

    def refreshTheme(self):
        self.setWidgetColors(
            self.backgroundColorString,
            self.textColorString,
            self.headerTextColorString,
            self.borderColorString,
        )

    def rightClickMenu(self, e: QPoint):
        menu = QMenu()

        if not self.isInLayout:
            if self.draggable:
                menu.addAction(
                    "Disable dragging",
                    lambda draggable=False: self.setDraggable(draggable),
                )
            else:
                menu.addAction(
                    "Enable dragging",
                    lambda draggable=True: self.setDraggable(draggable),
                )

            menu.addSeparator()
            menu.addAction("Delete", self.hide)
            menu.addSeparator()

        for source in self.sourceDictionary:
            if not self.sourceDictionary[source].hide_in_drop_down:
                submenu = menu.addMenu(source)
                available_sources = self.getAvailableSourceOptions(source)
                available_sources.sort()

                for option in available_sources:
                    if self.sourceDictionary[source].key_name == option:
                        submenu.addAction(
                            "--- {} ---".format(option),
                            lambda a=source, b=option: self.updateDictKeyTarget(a, b),
                        )  # If its the currently selected
                    else:
                        submenu.addAction(
                            "    {}".format(option),
                            lambda a=source, b=option: self.updateDictKeyTarget(a, b),
                        )

        menu.addSeparator()
        self.addCustomMenuItems(menu, e)
        menu.exec_(self.mapToGlobal(e))

    def addCustomMenuItems(self, menu: QMenu, e):
        pass

    def requestCallback(self, callback_name, callback_data):
        self.callbackEvents.append([callback_name, callback_data])

    def setDraggable(self, draggable):
        if not self.isInLayout:
            self.draggable = draggable

    def setWidgetColors(
        self, widget_background_string, text_string, header_text_string, border_string
    ):
        """Overwrite this for each widget"""
        self.setStyleSheet(
            "{0}{1}{2}{3}".format(
                widget_background_string, text_string, header_text_string, border_string
            )
        )

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        """Draw border around widget"""
        painter = QPainter(self)  # Grey background
        painter.setPen(
            QColor(self.borderColor[0], self.borderColor[1], self.borderColor[2])
        )
        painter.setBrush(
            QColor(
                self.backgroundColor[0],
                self.backgroundColor[1],
                self.backgroundColor[2],
            )
        )
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

    def coreUpdate(self):
        if not self.isInLayout:
            self.adjustSize()

        if self.isVisible():
            self.updateInFocus()

    def updateInFocus(self):
        """Called only when widget is being looked at"""
        pass

    def setVehicleData(self, vehicle_data, updated_data, recorded_data):
        """Called by the tab every loop.  DO NOT OVERRIDE"""
        self.recordedData = recorded_data
        self.vehicleData = vehicle_data
        self.updated_data_dictionary = updated_data
        self.updateData(vehicle_data, updated_data)

    def updateData(self, vehicle_data, updated_data):
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
        self.activeOffset = [
            float(e.screenPos().x()) - self.pos().x(),
            float(e.screenPos().y()) - self.pos().y(),
        ]

    def mouseMoveEvent(self, e: QMouseEvent):
        """Moves the active widget to the position of the mouse if we are currently clicked"""
        if not self.isInLayout and self.isClicked and self.draggable:
            x = clamp(
                e.screenPos().x() - self.activeOffset[0],
                0,
                self.parent().width() - self.width(),
            )
            y = clamp(
                e.screenPos().y() - self.activeOffset[1],
                0,
                self.parent().height() - self.height(),
            )
            self.move(x, y)

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.isClicked = False

    def addSourceKey(
        self,
        internal_id: str,
        value_type,
        default_key: str,
        default_value=None,
        hide_in_drop_down=False,
    ):
        self.sourceDictionary[internal_id] = SourceKeyData(
            default_key, value_type, default_value, hide_in_drop_down
        )

    def removeSourceKey(self, internal_key_id):
        del self.sourceDictionary[internal_key_id]

    def getDictValueUsingSourceKey(self, internal_key_id):
        dictionary_key = self.sourceDictionary[internal_key_id].key_name
        default_value = self.sourceDictionary[internal_key_id].default_value
        value_type = self.sourceDictionary[internal_key_id].value_type

        return_value = get_value_from_dictionary(
            self.vehicleData, dictionary_key, default_value
        )
        try:
            return value_type(return_value)
        except TypeError:
            return default_value

    def getRecordedDictDataUsingSourceKey(self, internal_key_id):
        dictionary_key = self.sourceDictionary[internal_key_id].key_name

        if dictionary_key in self.recordedData:
            return self.recordedData[dictionary_key]
        else:
            return [], []

    def isDictValueUpdated(self, internal_key_id):
        dictionary_key = self.sourceDictionary[internal_key_id].key_name

        if dictionary_key in self.updated_data_dictionary:
            return self.updated_data_dictionary[dictionary_key]
        else:
            return False

    def getValueIfUpdatedUsingSourceKey(self, internal_key_id):
        if self.isDictValueUpdated(internal_key_id):
            return self.getDictValueUsingSourceKey(internal_key_id)
        else:
            default_value = self.sourceDictionary[internal_key_id].default_value
            return default_value

    def updateDictKeyTarget(self, internal_key_id, new_key):
        self.sourceDictionary[internal_key_id].key_name = new_key

    def getAvailableSourceOptions(self, source):
        value_type = self.sourceDictionary[source].value_type
        option_list = []

        for key in self.vehicleData:
            if check_type(self.vehicleData[key], value_type):
                option_list.append(key)

        return option_list
