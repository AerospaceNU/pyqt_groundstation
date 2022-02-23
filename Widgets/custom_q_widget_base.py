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

from data_helpers import make_stylesheet_string, get_rgb_from_string, clamp


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

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.rightClickMenu)

    def setTheme(self, widgetBackground, text, headerText, border):
        """I implemented my own theme code instead of using the QT stuff, because this does what I want"""
        widgetBackgroundString = make_stylesheet_string("background", widgetBackground)
        textString = make_stylesheet_string("color", text)
        headerTextString = make_stylesheet_string("color", headerText)
        borderString = "border: {0}px solid {1};".format(1, border)

        self.borderColor = get_rgb_from_string(border)
        self.backgroundColor = get_rgb_from_string(widgetBackground)
        self.textColor = get_rgb_from_string(text)
        self.setWidgetColors(widgetBackgroundString, textString, headerTextString, borderString)

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

        self.addCustomMenuItems(menu)

        menu.exec_(self.mapToGlobal(e))

    def addCustomMenuItems(self, menu: QMenu):
        pass

    def requestCallback(self, callback_name, callback_data):
        self.callbackEvents.append([callback_name, callback_data])

    def setDraggable(self, draggable):
        if not self.isInLayout:
            self.draggable = draggable

    def setWidgetColors(self, widgetBackgroundString, textString, headerTextString, borderString):
        """Overwrite this for each widget"""
        self.setStyleSheet("{0}{1}{2}{3}".format(widgetBackgroundString, textString, headerTextString, borderString))

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        """Draw border around widget"""
        painter = QPainter(self)  # Grey background
        painter.setPen(QColor(self.borderColor[0], self.borderColor[1], self.borderColor[2]))
        painter.setBrush(QColor(self.backgroundColor[0], self.backgroundColor[1], self.backgroundColor[2]))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

    def coreUpdate(self):
        if not self.isInLayout:
            self.adjustSize()

    def updateData(self, vehicleData):
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
