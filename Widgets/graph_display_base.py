import os
# I don't even know anymore
os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")  # https://stackoverflow.com/questions/63829991/qt-qpa-plugin-could-not-load-the-qt-platform-plugin-xcb-in-even-though-it

from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt

from constants import Constants
from Widgets.custom_q_widget_base import CustomQWidgetBase
from data_helpers import get_value_from_dictionary, interpolate


class GraphDisplay(CustomQWidgetBase):
    series = QLineSeries()

    # Start Data should always be starting at 0, 0
    xTimePos = 0
    yAltitudePos = 0

    series.append(QPointF(xTimePos, yAltitudePos))

    def __init__(self, parentWidget: QWidget = None, pointsToKeep=200, updateInterval=3):
        super().__init__(parentWidget)

        self.updateInterval = updateInterval
        self.setWindowTitle("PyQtChart Line")
        self.setGeometry(100, 100, 680, 500)

        series = QLineSeries(self)

        # Start Data should always be starting at 0, 0
        xTimePos = 0
        yAltitudePos = 0

        series.append(xTimePos, yAltitudePos)

        # self.create_linechart()

        chart = QChart()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTitle("Line Chart Example")

        # Legend of Chart
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)

        layout = QGridLayout()
        layout.addWidget(chartview)
        self.setLayout(layout)

        self.show()

    def addPoint(self, point):
        self.series.append(point)
        self.create_linechart()

    def updateData(self, vehicleData):
        if "paths" not in vehicleData:
            paths = {}
        else:
            paths = vehicleData["paths"]

            self.paths = paths

            yTimePos = int(get_value_from_dictionary(vehicleData, Constants.altitude_key, 0))
            xTimePos = int(get_value_from_dictionary(vehicleData, Constants.timestamp_ms_key, 0))
            point = QPointF(xTimePos, yTimePos)

            # series append next point gotten from data
            self.addPoint(point)

        self.update()
        self.adjustSize()

# App = QApplication(sys.argv)
# sys.exit(App.exec_())
