"""
Widget for showing information about module
"""
from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QPushButton, QGridLayout

from src.Widgets.custom_q_widget_base import CustomQWidgetBase

from src.constants import Constants
from src.data_helpers import get_value_from_dictionary


class ModuleConfiguration(CustomQWidgetBase):
    def __init__(self, parent=None):
        super().__init__(widget=parent)

        self.moduleData = {}

        self.nameBoxList = []
        self.loadTimeBoxList = []
        self.enableButtonList = []
        self.hasRecordedDataBoxList = []
        self.moduleNameList = []

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(10, 5, 10, 5)

    def updateData(self, vehicle_data, updated_data):
        self.moduleData = get_value_from_dictionary(vehicle_data, Constants.module_data_key, {})

    def updateInFocus(self):
        i = 0
        for line_name in self.moduleData:
            line_data = self.moduleData[line_name]
            enabled = line_data[0]
            load_time = line_data[1]
            has_recorded_data = line_data[2]

            if i >= len(self.nameBoxList):
                name_box = QLabel()
                load_time_box = QLabel()
                enable_button = QPushButton()
                has_recorded_data_box = QLabel()

                layout_row = len(self.nameBoxList)
                self.layout.addWidget(name_box, layout_row, 0)
                self.layout.addWidget(load_time_box, layout_row, 1)
                self.layout.addWidget(enable_button, layout_row, 2)
                self.layout.addWidget(has_recorded_data_box, layout_row, 3)

                self.nameBoxList.append(name_box)
                self.loadTimeBoxList.append(load_time_box)
                self.enableButtonList.append(enable_button)
                self.hasRecordedDataBoxList.append(has_recorded_data_box)
                self.moduleNameList.append(line_name)

                enable_button.clicked.connect(lambda a, index=i: self.enableButtonCallback(a, index))

            self.setName(i, line_name)
            self.setLoadTime(i, load_time)
            self.setEnabledText(i, enabled)
            self.setHasRecordedData(i, has_recorded_data)

            i += 1

    def enableButtonCallback(self, a, button_index):
        module_name = self.moduleNameList[button_index]
        enabled = self.enableButtonList[button_index].text().lower() == "enabled"

        self.callbackEvents.append(["enable_module", "{0},{1}".format(module_name, not enabled)])

    def setName(self, index, name):
        name_box = self.nameBoxList[index]

        if name != name_box.text():
            name_box.setText(name)
            name_box.adjustSize()
            self.updateStyle(index)

    def setLoadTime(self, index, load_time):
        load_time = str(round(float(load_time), 5))
        load_time_box = self.loadTimeBoxList[index]
        box_text = "Load Time: {}s".format(load_time)

        if box_text != load_time_box.text():
            load_time_box.setText(box_text)
            load_time_box.adjustSize()
            self.updateStyle(index)

    def setEnabledText(self, index, enabled):
        if enabled:
            enabled_text = "Enabled"
        else:
            enabled_text = "Disabled"

        enabled_button = self.enableButtonList[index]

        if enabled_text != enabled_button.text():
            enabled_button.setText(enabled_text)

    def setHasRecordedData(self, index, has_recorded_data):
        box_text = "Has recorded data: {}".format(has_recorded_data)
        recorded_data_box = self.hasRecordedDataBoxList[index]

        if box_text != recorded_data_box.text():
            recorded_data_box.setText(box_text)
            recorded_data_box.adjustSize()
            self.updateStyle(index)

    def customUpdateAfterThemeSet(self):
        for i in range(len(self.nameBoxList)):
            self.updateStyle(i)

    def updateStyle(self, index):
        name_box = self.nameBoxList[index]
        load_time_box = self.loadTimeBoxList[index]
        has_recorded_data_box = self.hasRecordedDataBoxList[index]

        name_box.setAlignment(QtCore.Qt.AlignVCenter)
        name_box.setStyleSheet("font: 12pt")
        load_time_box.setAlignment(QtCore.Qt.AlignVCenter)
        load_time_box.setStyleSheet("font: 12pt")
        has_recorded_data_box.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        has_recorded_data_box.setStyleSheet("font: 12pt")
