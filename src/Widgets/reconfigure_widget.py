"""
Text box widget
"""

from PyQt5.QtWidgets import QComboBox, QGridLayout, QPushButton, QWidget

from src.constants import Constants
from src.data_helpers import get_value_from_list
from src.Widgets import custom_q_widget_base
from src.Widgets.QWidget_Parts import reconfigure_line_holder


class ReconfigureWidget(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.dropDownWidget = QComboBox()
        self.resetButton = QPushButton()
        self.reconfigureLineHolder = reconfigure_line_holder.ReconfigureLineHolder()
        self.reconfigureLineHolder.addCallback(self.textEntryCallback)

        self.resetButton.setText("Reset")
        self.resetButton.clicked.connect(self.resetCallback)

        layout = QGridLayout()
        layout.addWidget(self.dropDownWidget, 0, 0)
        layout.addWidget(self.resetButton, 0, 1)
        layout.addWidget(self.reconfigureLineHolder, 1, 0, 1, 2)
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

        if self.resetNeeded:
            lines = []

            for item in reconfigure_items:
                name = item[0]
                data_type = item[1]
                value = get_value_from_list(item, 2, "")
                description = get_value_from_list(item, 3, "")
                enum_vals = get_value_from_list(item, 4, "")

                lines.append(reconfigure_line_holder.ReconfigureLineDescription(name=name, type=data_type, value=value, description_text=description, enum_options=enum_vals))

            self.reconfigureLineHolder.setLineOptions(lines)
            self.resetNeeded = False
            self.adjustSize()

        self.reconfigureLineHolder.update()

    def resetCallback(self):
        self.resetNeeded = True
        self.callback_handler.requestCallback("{}_reset".format(self.source), True)

    def textEntryCallback(self, name, value):
        self.callback_handler.requestCallback("{}_set_new".format(self.source), "{0}:{1}:{2}".format(self.selectedTarget, name, value))

    def setMenuItems(self, menu_item_list):
        if len(menu_item_list) > 0:
            menu_item_list.sort()
        if menu_item_list != self.menuItems:
            self.dropDownWidget.clear()
            self.dropDownWidget.addItems(menu_item_list)
        self.menuItems = menu_item_list
