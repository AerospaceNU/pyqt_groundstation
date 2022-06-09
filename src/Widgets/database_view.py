"""
Starts up a scroll area that shows all the data in the database dictionary
"""
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QGridLayout, QScrollArea

from src.Widgets.custom_q_widget_base import CustomQWidgetBase


class DatabaseView(CustomQWidgetBase):
    def __init__(self, parent=None):
        super().__init__(widget=parent)

        self.scroll_area = QScrollArea()
        self.display_label = QLabel()
        self.scroll_area.setWidget(self.display_label)
        self.display_label.setFont(QFont("Monospace", 10))

        self.setMinimumWidth(500)
        self.setMinimumHeight(500)

        layout = QGridLayout()
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

    def updateData(self, vehicle_data, updated_data):
        string = ""

        for item in vehicle_data:
            string += "{}: {}\n".format(str(item), vehicle_data[item])

        self.display_label.setText(string)
        self.display_label.adjustSize()
