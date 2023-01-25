"""
Text box widget
"""

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout

from src.Widgets.custom_q_widget_base import CustomQWidgetBase
from src.Widgets.QWidget_Parts.two_column_text_display import TwoColumnTextDisplay
from src.constants import Constants


class TextBoxWidget(CustomQWidgetBase):
    def __init__(self, parent: QWidget = None, source_list=None, title="Text Box", font_size=12):
        super().__init__(parent)

        if source_list is None:
            source_list = []

        self.titleBox = QLabel()
        self.twoColumnDisplay = TwoColumnTextDisplay()

        layout = QGridLayout()
        layout.addWidget(self.titleBox)
        layout.addWidget(self.twoColumnDisplay)
        self.setLayout(layout)

        if type(source_list) == list:
            for i in range(len(source_list)):
                source = source_list[i]
                self.addSourceKey("line {}".format(i), str, source, default_value="No Data")
        elif type(source_list) == dict:
            keys_list = list(source_list.keys())

            for i in range(len(keys_list)):
                key = keys_list[i]
                source = source_list[key]
                self.addSourceKey("line {}".format(i), str, source, default_value="No Data", description=key)

        self.fontSize = font_size

        self.titleBox.setText(title)
        self.titleBox.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.titleBox.adjustSize()
        self.adjustSize()

    def addCustomMenuItems(self, menu, e):
        menu.addAction("Add Line", self.addLineToTextBox)
        remove_line_menu = menu.addMenu("Remove line")

        for key in self.sourceDictionary:  # Total hack to clear and recreate the legend
            remove_line_menu.addAction(self.sourceDictionary[key].key_name, lambda name=key: self.removeLineFromTextBox(name))

    def addLineToTextBox(self):
        num_keys = len(self.sourceDictionary.keys())
        self.addSourceKey("line {}".format(num_keys), str, "", default_value="No Data")

    def removeLineFromTextBox(self, line_name):
        self.removeSourceKey(line_name)

    def updateInFocus(self):
        column_1 = []
        column_2 = []
        for source_name in self.sourceDictionary:
            column_1.append(self.sourceDictionary[source_name].description)

            value = self.getDictValueUsingSourceKey(source_name)

            try:
                column_2.append(f"{float(value):.1f}")
            except:
                column_2.append(value)

        self.twoColumnDisplay.updateValues(column_1, column_2)
        self.adjustSize()

    def customUpdateAfterThemeSet(self):
        self.twoColumnDisplay.setStyleSheet(f"font: {self.fontSize}pt Monospace")
        self.titleBox.setStyleSheet(f"font: {self.fontSize}pt")


class CoreInformation(TextBoxWidget):
    def __init__(self, parent=None):
        keys = Constants()

        source_list = {"Altitude": keys.altitude_key,
                       "Vertical Speed": keys.vertical_speed_key,
                       "Latitude": keys.latitude_key,
                       "Longitude": keys.longitude_key,
                       }

        super().__init__(parent, source_list=source_list, title="Core Information", font_size=60)
