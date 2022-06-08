"""
Text box widget
"""

from PyQt5.QtWidgets import QComboBox, QGridLayout, QPushButton, QWidget

from src.constants import Constants
from src.data_helpers import get_value_from_list
from src.Widgets import custom_q_widget_base
from src.Widgets.QWidget_Parts import reconfigure_line


class ReconfigureWidget(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.dropDownWidget = QComboBox()
        self.resetButton = QPushButton()
        self.resetButton.setText("Reset")
        self.resetButton.clicked.connect(self.resetCallback)

        header = QWidget()
        header_layout = QGridLayout()
        header_layout.addWidget(self.dropDownWidget, 0, 0)
        header_layout.addWidget(self.resetButton, 0, 1)
        header.setLayout(header_layout)
        header.setContentsMargins(0, 0, 0, 0)

        layout = QGridLayout()
        layout.addWidget(header)
        self.setLayout(layout)

        self.source = Constants.primary_reconfigure
        self.selectedTarget = ""
        self.reconfigureWidgetLabels = []
        self.reconfigureWidgetTextEntry = []
        self.resetNeeded = False

        self.menuItems = []
        self.setMenuItems(["No data"])

    def updateData(self, vehicle_data, updated_data):
        if self.source not in vehicle_data:
            self.setMinimumSize(5, 5)
            return
        data_struct = vehicle_data[self.source]

        if len(data_struct) == 0:
            self.setMinimumSize(5, 5)
            return

        self.setMenuItems(list(data_struct.keys()))
        selected_target = self.dropDownWidget.currentText()
        if selected_target != self.selectedTarget:
            self.resetNeeded = True
            self.selectedTarget = selected_target

        if selected_target not in data_struct:
            return
        reconfigure_items = data_struct[selected_target]

        # If there's the wrong number of items, adjust the widget
        reset_needed = self.resetNeeded
        self.resetNeeded = False
        while len(reconfigure_items) > len(self.reconfigureWidgetLabels):
            line = reconfigure_line.ReconfigureLine()
            line.setText(reconfigure_items[len(self.reconfigureWidgetLabels)][0])
            line.setCallback(self.textEntryCallback)

            self.layout().addWidget(line)
            self.reconfigureWidgetLabels.append(line)
            reset_needed = True
        while len(reconfigure_items) < len(self.reconfigureWidgetLabels):
            self.layout().removeWidget(self.reconfigureWidgetLabels[-1])
            self.reconfigureWidgetLabels[-1].deleteLater()
            del self.reconfigureWidgetLabels[-1]
            reset_needed = True

        # Set text and labels on widgets
        for i in range(len(reconfigure_items)):
            text = reconfigure_items[i][0]
            type = reconfigure_items[i][1]
            value = get_value_from_list(reconfigure_items[i], 2, "")
            description = get_value_from_list(reconfigure_items[i], 3, "")
            config = get_value_from_list(reconfigure_items[i], 4, "")

            # Order matters here type then config then value
            self.reconfigureWidgetLabels[i].setText(text)
            self.reconfigureWidgetLabels[i].setType(type)
            self.reconfigureWidgetLabels[i].setDescription(description)
            self.reconfigureWidgetLabels[i].setConfig(config, force=reset_needed)
            self.reconfigureWidgetLabels[i].setValue(value, force=reset_needed)

        for line in self.reconfigureWidgetLabels:
            line.update()

    def resetCallback(self):
        self.resetNeeded = True
        self.callbackEvents.append(["{}_reset".format(self.source), True])

    def textEntryCallback(self, name, value):
        self.callbackEvents.append(["{}_set_new".format(self.source), "{0}:{1}:{2}".format(self.selectedTarget, name, value)])

    def setMenuItems(self, menu_item_list):
        if len(menu_item_list) > 0:
            menu_item_list.sort()
        if menu_item_list != self.menuItems:
            self.dropDownWidget.clear()
            self.dropDownWidget.addItems(menu_item_list)
        self.menuItems = menu_item_list

