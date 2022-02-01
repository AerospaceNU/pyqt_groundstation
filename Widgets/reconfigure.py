"""
Text box widget
"""

from PyQt5.QtWidgets import QWidget, QGridLayout, QComboBox, QPushButton

from Widgets import custom_q_widget_base

from Widgets.QWidget_Parts import reconfigure_line
from data_helpers import get_value_from_list


class Reconfigure(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parentWidget: QWidget = None):
        super().__init__(parentWidget)

        self.dropDownWidget = QComboBox()
        self.resetButton = QPushButton()
        self.resetButton.setText("Reset")
        self.resetButton.clicked.connect(self.resetCallback)

        header = QWidget()
        headerLayout = QGridLayout()
        headerLayout.addWidget(self.dropDownWidget, 0, 0)
        headerLayout.addWidget(self.resetButton, 0, 1)
        header.setLayout(headerLayout)
        header.setContentsMargins(0, 0, 0, 0)

        layout = QGridLayout()
        layout.addWidget(header)
        self.setLayout(layout)

        self.source = "reconfigure"
        self.selectedTarget = ""
        self.widgetBackgroundString = ""
        self.textString = ""
        self.headerTextString = ""
        self.borderString = ""
        self.reconfigureWidgetLabels = []
        self.reconfigureWidgetTextEntry = []
        self.resetNeeded = False

        self.menuItems = []
        self.setMenuItems(["No data"])

    def updateData(self, vehicleData):
        if self.source not in vehicleData:
            self.setMinimumSize(5, 5)
            return
        dataStruct = vehicleData[self.source]

        if len(dataStruct) == 0:
            self.setMinimumSize(5, 5)
            return

        self.setMenuItems(list(dataStruct.keys()))
        selectedTarget = self.dropDownWidget.currentText()
        if selectedTarget != self.selectedTarget:
            self.resetNeeded = True
            self.selectedTarget = selectedTarget

        if selectedTarget not in dataStruct:
            return
        reconfigureItems = dataStruct[selectedTarget]

        # If there's the wrong number of items, adjust the widget
        resetNeeded = self.resetNeeded
        self.resetNeeded = False
        while len(reconfigureItems) > len(self.reconfigureWidgetLabels):
            line = reconfigure_line.ReconfigureLine()
            line.setText(reconfigureItems[len(self.reconfigureWidgetLabels)][0])
            line.setCallback(self.textEntryCallback)

            self.layout().addWidget(line)
            self.reconfigureWidgetLabels.append(line)
            line.setColor(self.widgetBackgroundString, self.borderString, self.textString)
            resetNeeded = True
        while len(reconfigureItems) < len(self.reconfigureWidgetLabels):
            self.layout().removeWidget(self.reconfigureWidgetLabels[-1])
            self.reconfigureWidgetLabels[-1].deleteLater()
            del self.reconfigureWidgetLabels[-1]
            resetNeeded = True

        # Set text and labels on widgets
        for i in range(len(reconfigureItems)):
            text = reconfigureItems[i][0]
            type = reconfigureItems[i][1]
            value = get_value_from_list(reconfigureItems[i], 2, "")
            description = get_value_from_list(reconfigureItems[i], 3, "")
            config = get_value_from_list(reconfigureItems[i], 4, "")

            # Order matters here type then config then value
            self.reconfigureWidgetLabels[i].setText(text)
            self.reconfigureWidgetLabels[i].setType(type)
            self.reconfigureWidgetLabels[i].setDescription(description)
            self.reconfigureWidgetLabels[i].setConfig(config, force=resetNeeded)
            self.reconfigureWidgetLabels[i].setValue(value, force=resetNeeded)

        for line in self.reconfigureWidgetLabels:
            line.update()

    def resetCallback(self):
        self.resetNeeded = True
        self.callbackEvents.append(["{}_reconfigure_reset".format(self.tabName), True])

    def textEntryCallback(self, name, value):
        self.callbackEvents.append(["{}_reconfigure_set_new".format(self.tabName), "{0}:{1}:{2}".format(self.selectedTarget, name, value)])

    def setMenuItems(self, menuItemList):
        if len(menuItemList) > 0:
            menuItemList.sort()
        if menuItemList != self.menuItems:
            self.dropDownWidget.clear()
            self.dropDownWidget.addItems(menuItemList)
        self.menuItems = menuItemList
        self.dropDownWidget.setStyleSheet(self.widgetBackgroundString + self.headerTextString)

    def setWidgetColors(self, widgetBackgroundString, textString, headerTextString, borderString):
        self.widgetBackgroundString = widgetBackgroundString
        self.textString = textString
        self.headerTextString = headerTextString
        self.borderString = borderString
        self.dropDownWidget.setStyleSheet(widgetBackgroundString + headerTextString)
        self.resetButton.setStyleSheet(widgetBackgroundString + headerTextString)
