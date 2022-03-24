"""
Displays pyro continuity
"""

import PyQt5.QtCore as QtCore

from PyQt5.QtWidgets import QLabel, QGridLayout
from matplotlib.pyplot import title

from Widgets.custom_q_widget_base import CustomQWidgetBase
from constants import Constants


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
        self.titleWidget.setStyleSheet("background: black; color: white")
        layout.addWidget(self.titleWidget, 0, 0, 1, 6)

        width = 50
        height = 30

        self.annunciatorWidgets = []
        self.titleWidgets = []
        for column in range(Constants.MAX_PYROS):
            titleLabel = QLabel()
            titleLabel.setText(f"{column + 1}")
            layout.addWidget(titleLabel, 1, column)
            titleLabel.setStyleSheet("background: black; color: white")
            titleLabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
            titleLabel.setMinimumWidth(width)
            titleLabel.setMaximumWidth(width)
            titleLabel.setMaximumHeight(height)
            titleLabel.setMinimumHeight(height)
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
        if Constants.pyro_continuity not in vehicle_data:
            return

        pyro_cont = vehicle_data[Constants.pyro_continuity]
        if not pyro_cont.isdigit():
            pyro_cont = "0"
        
        pyro_cont = int(pyro_cont, 2)

        for i in range(Constants.MAX_PYROS):
            has_cont_b = (pyro_cont & 1 << i) > 0
            has_cont = "Yes" if has_cont_b else "No"

            if i >= len(self.annunciatorWidgets):
                break

            self.annunciatorWidgets[i].setText(has_cont)
            self.annunciatorWidgets[i].setToolTip(f"If pyro {i} has data")
            self.annunciatorWidgets[i].setToolTipDuration(5000)

            if has_cont_b:
                self.annunciatorWidgets[i].setStyleSheet("background: green; color: black")
            else:
                self.annunciatorWidgets[i].setStyleSheet("background: red; color: black")

        # for i in range(len(pyro_cont), len(self.annunciatorWidgets)):  # Make the rest red, no data or disconnected
        #     self.annunciatorWidgets[i].setText(" ")
        #     self.annunciatorWidgets[i].setStyleSheet("background: red; color: black")
        #     self.annunciatorWidgets[i].setText("No")

        if self.width() < self.annunciatorWidgets[0].width() * 2:  # Kind of a hack to force it to adjust properly when we have data
            self.setMaximumWidth(1000)
        self.adjustSize()
        self.setMaximumWidth(self.width())
        self.setMaximumHeight(self.height())
