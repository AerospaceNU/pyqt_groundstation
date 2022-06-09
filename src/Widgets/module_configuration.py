"""
Starts up a scroll area that shows all the data in the database dictionary
"""
from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QWidget, QPushButton

from src.Widgets.custom_q_widget_base import CustomQWidgetBase

from src.constants import Constants
from src.data_helpers import get_value_from_dictionary


class ModuleConfigLine(QWidget):
    def __init__(self):
        super(ModuleConfigLine, self).__init__()

        self.nameBox = QLabel()
        self.loadTimeBox = QLabel()
        self.enableButton = QPushButton()

        self.enableButton.setText("True")

        layout = QHBoxLayout()
        layout.addWidget(self.nameBox)
        layout.addWidget(self.loadTimeBox)
        layout.addWidget(self.enableButton)

        self.setLayout(layout)

    def setName(self, name):
        if name != self.nameBox.text():
            self.nameBox.setText(name)
            self.nameBox.adjustSize()
            self.updateStyle()

    def updateStyle(self):
        self.nameBox.setAlignment(QtCore.Qt.AlignVCenter)
        self.nameBox.setStyleSheet("font: 12pt")


class ModuleConfiguration(CustomQWidgetBase):
    def __init__(self, parent=None):
        super().__init__(widget=parent)

        self.listOfLines = []
        self.moduleData = {}

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def updateData(self, vehicle_data, updated_data):
        self.moduleData = get_value_from_dictionary(vehicle_data, Constants.module_data_key, {})

    def updateInFocus(self):
        i = 0
        for line_name in self.moduleData:
            line_data = self.moduleData[line_name]
            enabled = line_data[0]
            load_time = line_data[1]
            has_recorded_data = line_data[2]

            if i >= len(self.listOfLines):
                line_object = ModuleConfigLine()
                self.listOfLines.append(line_object)
                self.layout.addWidget(line_object)
                line_object.updateStyle()
                line_object.show()

            self.listOfLines[i].setName(line_name)

            i += 1

    def customUpdateAfterThemeSet(self):
        for line in self.listOfLines:
            line.updateStyle()
