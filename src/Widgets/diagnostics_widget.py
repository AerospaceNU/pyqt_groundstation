"""
Text box widget with a dropdown, one per packet type we can get down
"""

import time

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QComboBox, QGridLayout, QLabel, QWidget

from src.constants import Constants
from src.Widgets import custom_q_widget_base

MAX_TEXT_SELECTION_TIME = 20


class DiagnosticsWidget(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent: QWidget = None, auto_size=True, round_to_decimals=3):
        super().__init__(parent)

        self.textBoxWidget = QLabel()
        self.dropDownWidget = QComboBox()
        self.textBoxWidget.setFont(QFont("Monospace"))
        self.textBoxWidget.setTextInteractionFlags(Qt.TextSelectableByMouse)

        layout = QGridLayout()
        layout.addWidget(self.dropDownWidget)
        layout.addWidget(self.textBoxWidget)
        self.setLayout(layout)

        self.xBuffer = 0
        self.yBuffer = 0
        self.colorString = ""
        self.autoSize = auto_size
        self.round_to_decimals = round_to_decimals

        self.source = Constants.diagnostics_key

        self.menuItems = []
        self.setMenuItems(["No data"])

        self.selectionStartTime = time.time()

    def updateData(self, vehicle_data, updated_data):
        # Don't update if our dropdown has selected text
        if self.textBoxWidget.hasSelectedText():
            if self.selectionStartTime is None:
                self.selectionStartTime = time.time()

            # Deselect text in case you forget to do so manually
            if (time.time() - self.selectionStartTime) > MAX_TEXT_SELECTION_TIME:
                self.textBoxWidget.setSelection(0, 0)

            return
        else:
            self.selectionStartTime = None

        keys = list(vehicle_data.keys())
        keys = [key for key in keys if key.startswith(self.source)]

        if len(keys) <= 0:
            self.setMinimumSize(5, 5)
            return

        # Make dict of all the diagnostics panels so we have
        page_name_dict = {}
        for key in keys:
            page_name = key.split("/")[-1]
            page_name_dict[page_name] = key

        self.setMenuItems(list(page_name_dict.keys()))

        selected_target = self.dropDownWidget.currentText()

        if selected_target not in page_name_dict:
            return
        database_key = page_name_dict[selected_target]
        if database_key not in vehicle_data:
            return
        data_to_print = vehicle_data[database_key]

        out_string = ""
        longest_line = 0
        for line in data_to_print:
            line[0] = str(line[0]).replace("\t", "     ").rstrip()  # Do some formatting to convert tabs to spaces and ditch trailing spaces
            longest_line = max(longest_line, len(line[0]))

        for line in data_to_print:
            spaces = " " * (longest_line - len(line[0]) + 2)  # Add two extra spaces to everything

            # Try to round the value if we can
            value = str(line[1]).lstrip()
            try:
                value = str(round(float(value), self.round_to_decimals))
            except Exception:
                pass

            new_line = "{0}{2}{1}\n".format(line[0], value, spaces)

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
        self.textBoxWidget.setStyleSheet("font: 13pt Monospace")
