"""
Text box widget
"""

from PyQt5.QtWidgets import QLabel, QWidget, QGridLayout, QComboBox
from PyQt5.QtGui import QFont

from Widgets import custom_q_widget_base


class TextBoxDropDownWidget(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parentWidget: QWidget = None):
        super().__init__(parentWidget)

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

        self.source = "diagnostics"

        self.menuItems = []
        self.setMenuItems(["No data"])

    def updateData(self, vehicleData):
        if "diagnostics" not in vehicleData:
            self.setMinimumSize(5, 5)
            return
        dataStruct = vehicleData["diagnostics"]

        selectedTarget = self.dropDownWidget.currentText()
        menuItems = []
        for item in dataStruct:
            menuItems.append(item)
        self.setMenuItems(menuItems)

        if selectedTarget not in dataStruct:
            return
        dataToPrint = dataStruct[selectedTarget]

        outString = ""
        longestLine = 0
        for line in dataToPrint:
            line[0] = line[0].replace("\t", "     ").rstrip()  # Do some formatting to convert tabs to spaces and ditch trailing spaces
            longestLine = max(longestLine, len(line[0]))

        for line in dataToPrint:
            spaces = " " * (longestLine - len(line[0]) + 2)  # Add two extra spaces to everything
            newLine = "{0}{2}{1}\n".format(line[0], str(line[1]).lstrip(), spaces)

            outString = outString + newLine

        outString = outString[:-1]  # Remove last character

        self.textBoxWidget.setText(outString)
        self.adjustSize()

    def setMenuItems(self, menuItemList):
        if len(menuItemList) > 0:
            menuItemList.sort()
        if menuItemList != self.menuItems:
            self.dropDownWidget.clear()
            self.dropDownWidget.addItems(menuItemList)
        self.menuItems = menuItemList
        self.dropDownWidget.setStyleSheet(self.colorString)

    def setWidgetColors(self, widgetBackgroundString, textString, headerTextString, borderString):
        self.colorString = widgetBackgroundString + headerTextString
        self.textBoxWidget.setStyleSheet(widgetBackgroundString + textString)
        self.dropDownWidget.setStyleSheet(widgetBackgroundString + headerTextString)
