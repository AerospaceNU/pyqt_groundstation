"""
Widget for buttons
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QComboBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)
from qtrangeslider import QRangeSlider

from src.Widgets import custom_q_widget_base


class GraphTabControl(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, widget: QWidget = None):
        super().__init__(widget)
        self.resetGraphButton = QPushButton()

        self.enableGraphButton = QPushButton()
        self.enableGraphButton.clicked.connect(self.onEnableButtonClick)
        self.recordedDataModeSelect = QComboBox()
        self.enableGraphButton.setText("Disable Graph Updating")
        self.historyLabelBox = QLabel()
        self.historyTextBox = QLineEdit()

        self.rangeSlider = QRangeSlider(Qt.Horizontal)
        self.rangeSlider.setRange(0, 1000)
        self.rangeSlider.setSliderPosition([0, 1000])
        self.historyTextBox.setMaximumWidth(100)

        self.graphs_enabled = True

        layout = QGridLayout()
        layout.addWidget(self.resetGraphButton, 1, 1)
        layout.addWidget(self.enableGraphButton, 1, 2)
        layout.addWidget(self.recordedDataModeSelect, 1, 3)
        layout.addWidget(self.rangeSlider, 1, 4)
        layout.addWidget(self.historyLabelBox, 1, 5)
        layout.addWidget(self.historyTextBox, 1, 6)
        self.setLayout(layout)

        font = QFont("Monospace", 10)
        self.resetGraphButton.setFont(font)
        self.enableGraphButton.setFont(font)
        self.historyLabelBox.setFont(font)
        self.recordedDataModeSelect.setFont(font)
        self.resetGraphButton.setText("Clear Graphs")
        self.historyLabelBox.setText("History Length (seconds):")
        self.recordedDataModeSelect.addItems(["Live Data", "Playback"])

    def setRange(self, min_value, max_value):
        self.rangeSlider.setRange(min_value, max_value)

    def playbackEnabled(self):
        return self.recordedDataModeSelect.currentText().lower() == "playback"

    def getHistoryBoxValue(self):
        return self.historyTextBox.text()

    def onEnableButtonClick(self):
        self.graphs_enabled = not self.graphs_enabled
        if self.graphs_enabled:
            self.enableGraphButton.setText("Disable Graph Updating")
        else:
            self.enableGraphButton.setText("Enable Graph Updating")

    def graphsEnabled(self):
        return self.graphs_enabled

    def setWidgetColors(self, widget_background_string, text_string, header_text_string, border_string):
        string = "{0}{1}{2}{3}".format(widget_background_string, text_string, header_text_string, border_string)
        self.setStyleSheet("QWidget#" + self.objectName() + "{" + string + "}")

        self.resetGraphButton.setStyleSheet(widget_background_string + text_string)
        self.enableGraphButton.setStyleSheet(widget_background_string + text_string)
        self.rangeSlider.setStyleSheet(text_string)
        self.historyLabelBox.setStyleSheet(widget_background_string + text_string)
        self.historyTextBox.setStyleSheet(border_string + widget_background_string + text_string)
        self.recordedDataModeSelect.setStyleSheet(widget_background_string + text_string)
