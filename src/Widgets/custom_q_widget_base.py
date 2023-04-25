"""
Custom base QWidget

Handles everything that is needed to be common between widgets
"""

import os
import logging

from PyQt5 import QtGui
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QFrame, QMenu, QWidget

from src.callback_handler import CallbackHandler
from src.config import ConfigSaver
from src.CustomLogging.dpf_logger import MAIN_GUI_LOGGER
from src.data_helpers import check_type, clamp, get_value_from_dictionary, get_info_color_palette_from_background, InfoColorPalette, get_text_from_qcolor, get_well_formatted_rgb_string


class SourceKeyData(object):
    """Data structure to hold info about a source key thingy"""

    def __init__(self, key_name, value_type, default_value, hide_in_drop_down, description):
        self.key_name = key_name
        self.value_type = value_type
        self.default_value = default_value
        self.hide_in_drop_down = hide_in_drop_down

        if description == "":
            self.description = self.key_name
        else:
            self.description = description


class CustomQWidgetBase(QFrame):
    def __init__(self, widget: QWidget = None):
        super().__init__(widget)

        self.widgetSettings = ConfigSaver(self.__class__.__name__)
        self.logger: logging.Logger = MAIN_GUI_LOGGER.get_logger(self.__class__.__name__)
        self.callback_handler = CallbackHandler()

        self.isInLayout = widget is None
        self.isClosed = False
        self.isClicked = False
        self.draggable = True
        self.activeOffset = [0, 0]

        self.textColor = ""
        self.headerTextColor = ""
        self.okColor = ""
        self.warnColor = ""
        self.errorColor = ""

        self.vehicleData = {}
        self.recordedData = {}
        self.updated_data_dictionary = {}  # Tracks which keys are new since the last GUI loop
        self.sourceDictionary = {}

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.rightClickMenu)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        super().closeEvent(a0)
        self.isClosed = True
        self.callback_handler.closeOut()

    def popOut(self):
        """
        Hide ourself and ask the base GUI to make a new copy in a new window
        """

        # We used to hide ourselves, but that's a bit annoying unless we
        # set up a way to pop widgets back in
        # self.hide()

        # Little sketchy but whatever -- give the callback the clazz to instantiate
        self.callback_handler.requestCallback("create_widget_new_window", self.__class__)

    def rightClickMenu(self, e: QPoint):
        menu = QMenu()

        menu.addAction("Pop into own window", self.popOut)

        if not self.isInLayout:
            if self.draggable:
                menu.addAction("Disable dragging", lambda draggable=False: self.setDraggable(draggable))
            else:
                menu.addAction("Enable dragging", lambda draggable=True: self.setDraggable(draggable))

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
                        submenu.addAction("--- {} ---".format(option), lambda a=source, b=option: self.updateDictKeyTarget(a, b))  # If its the currently selected
                    else:
                        submenu.addAction("    {}".format(option), lambda a=source, b=option: self.updateDictKeyTarget(a, b))

        menu.addSeparator()
        self.addCustomMenuItems(menu, e)
        menu.exec_(self.mapToGlobal(e))

    def addCustomMenuItems(self, menu: QMenu, e):
        pass

    def requestCallback(self, callback_name, callback_data):
        self.callback_handler.requestCallback(callback_name, callback_data)

    def setDraggable(self, draggable):
        if not self.isInLayout:
            self.draggable = draggable

    def updateAfterThemeSet(self):
        """Allows custom appearances to be set across all widgets"""

        self.textColor = get_text_from_qcolor(self.palette().text().color())
        self.headerTextColor = os.getenv("QTMATERIAL_PRIMARYCOLOR")
        self.okColor = get_well_formatted_rgb_string(self.getInfoColorPalette().info_color)
        self.warnColor = get_well_formatted_rgb_string(self.getInfoColorPalette().warn_color)
        self.errorColor = get_well_formatted_rgb_string(self.getInfoColorPalette().error_color)

        self.customUpdateAfterThemeSet()

        # if self.isInLayout:
        #     self.setStyleSheet("QWidget#" + self.objectName() + " {border: 0}")

    def getInfoColorPalette(self) -> InfoColorPalette:
        return get_info_color_palette_from_background(self.palette().base().color())

    def customUpdateAfterThemeSet(self):
        """Overwrite this for each widget"""
        return

    def coreUpdate(self):
        if not self.isInLayout:
            self.adjustSize()

        if self.isVisible():
            self.updateInFocus()

    def updateInFocus(self):
        """Called only when widget is being looked at"""
        pass

    def updateVehicleData(self, vehicle_data, console_data, updated_data):
        """Called by the tab every loop.  DO NOT OVERRIDE"""
        self.vehicleData = vehicle_data
        self.updated_data_dictionary = updated_data
        self.updateData(vehicle_data, updated_data)
        self.updateConsole(console_data)
        self.coreUpdate()

        return []

    def setRecordedData(self, recorded_data):
        self.recordedData = recorded_data

    def updateData(self, vehicle_data, updated_data):
        """Called every loop with new vehicle database dictionary"""
        pass

    def updateConsole(self, data):
        pass

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

    def addSourceKey(self, internal_id: str, value_type, default_key: str, default_value=None, hide_in_drop_down=False, description=""):
        self.sourceDictionary[internal_id] = SourceKeyData(default_key, value_type, default_value, hide_in_drop_down, description)

    def removeSourceKey(self, internal_key_id):
        del self.sourceDictionary[internal_key_id]

    def getDictValueUsingSourceKey(self, internal_key_id):
        dictionary_key = self.sourceDictionary[internal_key_id].key_name
        default_value = self.sourceDictionary[internal_key_id].default_value
        value_type = self.sourceDictionary[internal_key_id].value_type

        return_value = get_value_from_dictionary(self.vehicleData, dictionary_key, default_value)

        if type(return_value) == value_type:
            return return_value
        elif return_value is None:
            return None
        else:
            try:
                return value_type(return_value)
            except (TypeError, ValueError):
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
