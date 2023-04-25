"""
Text box widget
"""

import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import QGridLayout, QLabel

from src.Widgets.custom_q_widget_base import CustomQWidgetBase


class AnnunciatorPanel(CustomQWidgetBase):
    def __init__(self, parent_widget=None):
        super().__init__(parent_widget)

        self.xBuffer = 0
        self.yBuffer = 0

        self.rows = 10
        self.columns = 2
        self.title = "Test"
        self.source = "annunciator_1"

        layout = QGridLayout()
        self.titleWidget = QLabel()
        self.titleWidget.setText(self.title)
        self.titleWidget.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        # layout.addWidget(self.titleWidget, 0, 0, 1, self.columns)

        self.annunciatorWidgets = []
        for column in range(self.columns):
            for row in range(self.rows):
                self.annunciatorWidgets.append(QLabel())
                self.annunciatorWidgets[-1].setMaximumWidth(150)
                self.annunciatorWidgets[-1].setMaximumHeight(20)
                self.annunciatorWidgets[-1].setMinimumWidth(150)
                layout.addWidget(self.annunciatorWidgets[-1], row, column)

        self.setLayout(layout)

    def updateData(self, vehicle_data, updated_data):
        if self.source not in vehicle_data:
            self.setMaximumWidth(100)
            return
        data = vehicle_data[self.source]

        for i in range(len(data)):
            if i >= len(self.annunciatorWidgets):
                break

            self.annunciatorWidgets[i].setText(data[i][0])
            self.annunciatorWidgets[i].setToolTip(data[i][2])
            self.annunciatorWidgets[i].setToolTipDuration(5000)

            status = str(data[i][1])
            if status == "0":
                self.annunciatorWidgets[i].setStyleSheet(f"background: {self.okColor}; color: black")
            elif status == "1":
                self.annunciatorWidgets[i].setStyleSheet(f"background: {self.warnColor}; color: black")
            elif status == "2":
                self.annunciatorWidgets[i].setStyleSheet(f"background: {self.errorColor}; color: black")
            else:
                self.annunciatorWidgets[i].setStyleSheet("background: blue; color: black")

        for i in range(len(data), len(self.annunciatorWidgets)):  # Make the rest empty and green
            self.annunciatorWidgets[i].setText(" ")
            self.annunciatorWidgets[i].setStyleSheet(f"background: {self.okColor}; color: black")

        if self.width() < self.annunciatorWidgets[0].width() * 2:  # Kind of a hack to force it to adjust properly when we have data
            self.setMaximumWidth(1000)
        self.adjustSize()
        self.setMaximumWidth(self.width())
        self.setMaximumHeight(self.height())
