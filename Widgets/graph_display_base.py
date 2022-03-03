import os
import time

# I don't even know anymore
os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")  # https://stackoverflow.com/questions/63829991/qt-qpa-plugin-could-not-load-the-qt-platform-plugin-xcb-in-even-though-it

from PyQt5.QtWidgets import QWidget, QGridLayout
from pyqtgraph import PlotWidget

from constants import Constants
from Widgets.custom_q_widget_base import CustomQWidgetBase
from data_helpers import get_value_from_dictionary, interpolate


class GraphDisplay(CustomQWidgetBase):
    def __init__(self, parentWidget: QWidget = None, pointsToKeep=200):
        super().__init__(parentWidget)

        self.setGeometry(100, 100, 680, 500)

        self.graphWidget = PlotWidget()
        self.graphWidget.setTitle("Altitude")
        self.graphWidget.setLabel('bottom', "Time (s)")

        self.time_list = []
        self.value_list = []
        self.start_time = time.time()

        self.data_line = self.graphWidget.plot(self.time_list, self.value_list)

        layout = QGridLayout()
        layout.addWidget(self.graphWidget)
        self.setLayout(layout)

        self.show()

    def updateData(self, vehicleData):
        altitude = float(get_value_from_dictionary(vehicleData, Constants.altitude_key, 0))

        self.time_list.append(time.time() - self.start_time)
        self.value_list.append(altitude)

        self.data_line.setData(self.time_list, self.value_list)
