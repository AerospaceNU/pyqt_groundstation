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

        self.title = "Pyro Cont"

        layout = QGridLayout()
        self.titleWidget = QLabel()
        self.titleWidget.setText(self.title)
        self.titleWidget.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        # layout.addWidget(self.titleWidget, 0, 0, 1, self.columns)

        self.annunciatorWidgets = []
        self.titleWidgets = []
        for column in range(Constants.MAX_PYROS):
            titleLabel = QLabel()
            titleLabel.setText(f"{column + 1}")
            layout.addWidget(titleLabel, 0, column)
            titleLabel.setStyleSheet("background: black; color: white")
            self.titleWidgets.append(titleLabel)

            self.annunciatorWidgets.append(QLabel())
            self.annunciatorWidgets[-1].setMaximumWidth(100)
            self.annunciatorWidgets[-1].setMaximumHeight(20)
            self.annunciatorWidgets[-1].setMinimumWidth(70)
            layout.addWidget(self.annunciatorWidgets[-1], 1, column)

        self.setLayout(layout)

    def updateData(self, vehicle_data, updated_data):
        if Constants.pyro_continuity not in vehicle_data:
            self.setMaximumWidth(100)
            return

        pyro_cont = vehicle_data[Constants.pyro_continuity]
        pyro_cont = '1100'

        for i in range(len(pyro_cont)):
            has_cont_b = pyro_cont[i] == '1'
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

        for i in range(len(pyro_cont), len(self.annunciatorWidgets)):  # Make the rest red, no data or disconnected
            self.annunciatorWidgets[i].setText(" ")
            self.annunciatorWidgets[i].setStyleSheet("background: red; color: black")
            self.annunciatorWidgets[i].setText("No")

        if self.width() < self.annunciatorWidgets[0].width() * 2:  # Kind of a hack to force it to adjust properly when we have data
            self.setMaximumWidth(1000)
        self.adjustSize()
        self.setMaximumWidth(self.width())
        self.setMaximumHeight(self.height())
