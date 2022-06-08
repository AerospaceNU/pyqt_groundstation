"""
Starts up a scroll area that shows all the data in the database dictionary
"""
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QGridLayout, QScrollArea

from src.Widgets.MainTabs.main_tab_common import TabCommon


class DatabaseViewTab(TabCommon):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.scroll_area = QScrollArea()
        self.display_label = QLabel()
        self.scroll_area.setWidget(self.display_label)
        self.display_label.setFont(QFont("Monospace", 10))

        layout = QGridLayout()
        layout.addWidget(self.scroll_area)
        layout.setContentsMargins(1, 1, 1, 1)
        self.setLayout(layout)

    def customUpdateVehicleData(self, data):
        string = ""

        for item in data:
            string += "{}: {}\n".format(str(item), data[item])

        self.display_label.setText(string)
        self.display_label.adjustSize()
