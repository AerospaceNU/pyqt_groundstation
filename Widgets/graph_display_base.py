
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import QApplication, QWidget
from Widgets import custom_q_widget_base
import sys
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt

from constants import Constants
from data_helpers import get_value_from_dictionary


class GraphDisplay(custom_q_widget_base.CustomQWidgetBase):
    series = QLineSeries()

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

        self.setCentralWidget(chartview)

        self.show()

        #self.create_linechart()


# Data for Linechart
    def create_linechart(self):
        series = QLineSeries(self)
        series.append(0, 6)
        series.append(2, 4)
        series.append(3, 8)
        series.append(7, 4)
        series.append(10, 5)

        series << QPointF(11, 1) << QPointF(13, 3) << QPointF(17, 6) << QPointF(18, 3) << QPointF(20, 2)

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

        self.setCentralWidget(chartview)


    def addPoint(self, point):
        self.series.append(point)
        #self.xCenter =
        self.create_linechart()


    def updateData(self, vehicleData):
        if "paths" not in vehicleData:
            paths = {}
        else:
            paths = vehicleData["paths"]

            self.paths = paths

            xTimePos = int(get_value_from_dictionary(vehicleData, Constants.altitude_key, 0))
            yTimePos = int(get_value_from_dictionary(vehicleData, Constants.timestamp_ms_key, 0))

            point = QPointF(xTimePos, yTimePos)

            # series append next point gotten from data
            self.addPoint(point)

        self.update()
        self.adjustSize()



#App = QApplication(sys.argv)
#sys.exit(App.exec_())