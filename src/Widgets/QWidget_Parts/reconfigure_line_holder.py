"""
Holds multiple reconfigure lines and has logic to change number shown on the fly
"""

from dataclasses import dataclass
from typing import List

from PyQt5.QtWidgets import QVBoxLayout, QWidget

from src.Widgets.QWidget_Parts import reconfigure_line


@dataclass
class ReconfigureLineDescription:
    name: str
    type: str
    value: str
    enum_options: List[str]
    description_text: str = ""


class ReconfigureLineHolder(QWidget):
    def __init__(self, parent=None):
        super(ReconfigureLineHolder, self).__init__(parent=parent)

        self.setLayout(QVBoxLayout())

        self.reconfigureLines: List[reconfigure_line.ReconfigureLine] = []
        self.callbacks = []

    def addCallback(self, callback):
        self.callbacks.append(callback)

    def onValueChanged(self, name, value):
        for callback in self.callbacks:
            try:
                callback(name, value)
            except Exception as e:
                print(e)

    def setLineOptions(self, lines: List[ReconfigureLineDescription]):
        # If there's the wrong number of items, adjust the widget
        while len(lines) > len(self.reconfigureLines):
            line = reconfigure_line.ReconfigureLine()
            line.setText(lines[len(self.reconfigureLines)].name)
            line.setCallback(self.onValueChanged)

            self.layout().addWidget(line)
            self.reconfigureLines.append(line)
        while len(lines) < len(self.reconfigureLines):
            self.layout().removeWidget(self.reconfigureLines[-1])
            self.reconfigureLines[-1].deleteLater()
            del self.reconfigureLines[-1]

        # Set text and labels on widgets
        for i in range(len(lines)):
            text = lines[i].name
            data_type = lines[i].type
            value = lines[i].value
            description = lines[i].description_text
            config = lines[i].enum_options

            # Order matters here type then config then value
            self.reconfigureLines[i].setText(text)
            self.reconfigureLines[i].setType(data_type)
            self.reconfigureLines[i].setDescription(description)
            self.reconfigureLines[i].setConfig(config, force=True)
            self.reconfigureLines[i].setValue(value, force=True)

        for line in self.reconfigureLines:
            line.update()

        self.adjustSize()

    def update(self) -> None:
        for line in self.reconfigureLines:
            line.update()

    def getData(self):
        out_dict = {}

        for line in self.reconfigureLines:
            out_dict[line.getName()] = line.getValue()

        return out_dict
