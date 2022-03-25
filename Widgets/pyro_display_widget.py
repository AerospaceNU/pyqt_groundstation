"""
Displays pyro continuity
"""

import PyQt5.QtCore as QtCore

from PyQt5.QtWidgets import QLabel, QGridLayout

from data_helpers import get_value_from_dictionary
from constants import Constants

from Widgets.custom_q_widget_base import CustomQWidgetBase


class PyroWidget(CustomQWidgetBase):
    def __init__(self, parent_widget=None):
        super().__init__(parent_widget)

        self.xBuffer = 0
        self.yBuffer = 0

        self.title = "Pyro Continuity Status"

        layout = QGridLayout()
        self.titleWidget = QLabel()
        self.titleWidget.setText(self.title)
        self.titleWidget.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        layout.addWidget(self.titleWidget, 0, 0, 1, 6)

        width = 50
        height = 30

        self.annunciatorWidgets = []
        self.titleWidgets = []
        for column in range(Constants.MAX_PYROS):
            titleLabel = QLabel()
            titleLabel.setText(f"{column + 1}")
            layout.addWidget(titleLabel, 1, column)
            titleLabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
            self.titleWidgets.append(titleLabel)

            self.annunciatorWidgets.append(QLabel())
            self.annunciatorWidgets[-1].setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
            self.annunciatorWidgets[-1].setMaximumWidth(width)
            self.annunciatorWidgets[-1].setMaximumHeight(height)
            self.annunciatorWidgets[-1].setMinimumHeight(height)
            self.annunciatorWidgets[-1].setMinimumWidth(width)
            layout.addWidget(self.annunciatorWidgets[-1], 2, column)

        self.setLayout(layout)

    def updateData(self, vehicle_data, updated_data):
        pyro_cont_list = get_value_from_dictionary(vehicle_data, Constants.pyro_continuity, [])

        for i in range(len(pyro_cont_list)):
            pyro = pyro_cont_list[i]
            has_cont = "Yes" if pyro else "No"

            if i >= len(self.annunciatorWidgets):
                break

            self.annunciatorWidgets[i].setText(has_cont)
            self.annunciatorWidgets[i].setToolTip(f"If pyro {i} has data")
            self.annunciatorWidgets[i].setToolTipDuration(5000)

            if pyro:
                self.annunciatorWidgets[i].setStyleSheet("background: green; color: black")
            else:
                self.annunciatorWidgets[i].setStyleSheet("background: red; color: black")

        if self.width() < self.annunciatorWidgets[0].width() * 2:  # Kind of a hack to force it to adjust properly when we have data
            self.setMaximumWidth(1000)
        self.adjustSize()
        self.setMaximumWidth(self.width())
        self.setMaximumHeight(self.height())

    def setWidgetColors(self, widget_background_string, text_string, header_text_string, border_string):
        self.setStyleSheet("QWidget#" + self.objectName() + " {" + widget_background_string + text_string + border_string + "}")
        self.titleWidget.setStyleSheet(widget_background_string + header_text_string)

        for widget in self.titleWidgets:
            widget.setStyleSheet(widget_background_string + text_string)
