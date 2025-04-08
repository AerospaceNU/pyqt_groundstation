from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QFont, QColor
from PyQt5.QtChart import QChart, QChartView, QHorizontalBarSeries, QBarSet, QValueAxis

from src.Widgets.custom_q_widget_base import CustomQWidgetBase
from src.constants import Constants

class LandingSiteTemperatureWidget(CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None, source_list=None, default_temperature=0):
        super().__init__(parent_widget)

        # Register the temperature source key
        self.addSourceKey(
            "payload_landing_site_temperature",
            float,
            Constants.payload_landing_site_temperature_key,
            default_value=0,
            hide_in_drop_down=True
        )

        # Initialize temperature bar
        self.temp = 10
        self.bar_set = QBarSet(f"Temperature: {self.temp} °C")
        self.bar_set.append(self.temp)
        self.bar_set.setColor(QColor(255, 0, 0))

        # Apply font to bar label
        self.label_font = QFont()
        self.label_font.setPointSize(18)
        self.bar_set.setLabelFont(self.label_font)

        # Create horizontal bar series
        self.series = QHorizontalBarSeries()
        self.series.append(self.bar_set)

        # Create and configure chart
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle("Payload Landing Site Temperature")
        title_font = QFont()
        title_font.setPointSize(20)
        self.chart.setTitleFont(title_font)
        self.chart.legend().setFont(self.label_font)
        self.chart.setBackgroundBrush(Qt.transparent)

        # Create X-axis for temperature values
        self.axis_x = QValueAxis()
        self.axis_x.setRange(0, 150)
        self.axis_x.setTickCount(4)
        self.axis_x.setTickInterval(50)
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.series.attachAxis(self.axis_x)

        # Chart view settings
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setStyleSheet("background-color: #f5f5f5; border: none;")

        # Layout setup
        layout = QVBoxLayout(self)
        layout.addWidget(self.chart_view)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Widget appearance
        self.setStyleSheet("border: none;")
        self.resize(400, 200)

    def updateData(self, vehicle_data, updated_data):
        # Update temperature value and label
        temp = self.getDictValueUsingSourceKey("payload_landing_site_temperature")
        self.bar_set.replace(0, temp)
        self.bar_set.setLabel(f"Temperature: {temp} °C")
        self.chart_view.update()