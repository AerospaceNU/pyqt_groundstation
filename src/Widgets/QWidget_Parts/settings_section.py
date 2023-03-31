from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QLabel

from src.Widgets.QWidget_Parts.reconfigure_line_holder import ReconfigureLineHolder


class SettingsSection(ReconfigureLineHolder):
    def __init__(self, parentWidget: QWidget = None):
        super().__init__(parentWidget)

        self.titleBox = QLabel()
        self.titleBox.setAlignment(QtCore.Qt.AlignCenter)
        self.layout().addWidget(self.titleBox)

        self.sectionName = ""

    def setName(self, name):
        self.sectionName = name
        self.titleBox.setText(name)

    def onValueChanged(self, name, value):
        for callback in self.callbacks:
            try:
                callback(self.sectionName, name, value)
            except Exception as e:
                print(e)
