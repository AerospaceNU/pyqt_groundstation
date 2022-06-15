"""
Text box widget
"""

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QComboBox, QGridLayout, QLabel, QWidget

from src.constants import Constants
from src.Widgets import custom_q_widget_base


class TextBoxDropDownWidget(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent: QWidget = None, auto_size=True):
        super().__init__(parent)

        self.textBoxWidget = QLabel()
        self.dropDownWidget = QComboBox()
        self.textBoxWidget.setFont(QFont("Monospace"))

        layout = QGridLayout()
        layout.addWidget(self.dropDownWidget)
        layout.addWidget(self.textBoxWidget)
        self.setLayout(layout)

        self.xBuffer = 0
        self.yBuffer = 0
        self.colorString = ""
        self.autoSize = True

        self.source = Constants.raw_message_data_key

        self.menuItems = []
        self.setMenuItems(["No data"])

    def updateData(self, vehicle_data, updated_data):
        if self.source not in vehicle_data:
            self.setMinimumSize(5, 5)
            return
        data_struct = vehicle_data[self.source]

        selected_target = self.dropDownWidget.currentText()
        menu_items = []
        for item in data_struct:
            menu_items.append(item)
        self.setMenuItems(menu_items)

        if selected_target not in data_struct:
            return
        data_to_print = data_struct[selected_target]

        out_string = ""
        longest_line = 0
        for line in data_to_print:
            line[0] = str(line[0]).replace("\t", "     ").rstrip()  # Do some formatting to convert tabs to spaces and ditch trailing spaces
            longest_line = max(longest_line, len(line[0]))

        for line in data_to_print:
            spaces = " " * (longest_line - len(line[0]) + 2)  # Add two extra spaces to everything
            new_line = "{0}{2}{1}\n".format(line[0], str(line[1]).lstrip(), spaces)

            out_string = out_string + new_line

        out_string = out_string[:-1]  # Remove last character

        self.textBoxWidget.setText(out_string)
        if self.autoSize:
            self.adjustSize()

    def setMenuItems(self, menu_item_list):
        if len(menu_item_list) > 0:
            menu_item_list.sort()
        if menu_item_list != self.menuItems:
            self.dropDownWidget.clear()
            self.dropDownWidget.addItems(menu_item_list)
        self.menuItems = menu_item_list
        self.dropDownWidget.setStyleSheet(self.colorString)

    def customUpdateAfterThemeSet(self):
        self.textBoxWidget.setStyleSheet("font: 10pt Monospace")
