"""
Widget for buttons
"""

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton
from PyQt5.QtCore import Qt
from qtrangeslider import QRangeSlider

from Widgets import custom_q_widget_base


class GraphTabControl(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, widget: QWidget = None):
        super().__init__(widget)
        self.resetGraphButton = QPushButton()
        self.rangeSlider = QRangeSlider(Qt.Horizontal)
        self.rangeSlider.setRange(0, 1000)
        self.rangeSlider.setSliderPosition([0, 1000])

        self.slider_min = 0
        self.slider_max = 1

        layout = QGridLayout()
        layout.addWidget(self.resetGraphButton, 1, 1)
        layout.addWidget(self.rangeSlider, 1, 2)
        self.setLayout(layout)

        font = QFont("Monospace", 8)
        self.resetGraphButton.setFont(font)
        self.resetGraphButton.setText("Clear Graphs")

    def setRange(self, min_value, max_value):
        self.rangeSlider.setRange(min_value, max_value)

    def setWidgetColors(self, widget_background_string, text_string, header_text_string, border_string):
        string = "{0}{1}{2}{3}".format(widget_background_string, text_string, header_text_string, border_string)
        self.setStyleSheet("QWidget#" + self.objectName() + "{" + string + "}")

        self.resetGraphButton.setStyleSheet(widget_background_string + text_string)
        self.rangeSlider.setStyleSheet(text_string)
