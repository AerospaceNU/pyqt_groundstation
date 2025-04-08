from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtCore import Qt
from src.Widgets.custom_q_widget_base import CustomQWidgetBase
from src.constants import Constants
from src.Widgets.QWidget_Parts import simple_bar_graph_widget
from PyQt5.QtChart import QChart, QChartView, QHorizontalBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PyQt5.QtGui import QPainter  # Add this import at the top of your script
import numpy as np

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtChart import QChart, QChartView, QHorizontalBarSeries, QBarSet
from PyQt5.QtGui import QPainter, QFont
from PyQt5.QtGui import QColor

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtChart import QChart, QChartView, QHorizontalBarSeries, QBarSet, QValueAxis
from PyQt5.QtGui import QPainter  # Add this import at the top of your script
from PyQt5.QtCore import Qt

from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtChart import QChart, QChartView, QHorizontalBarSeries, QBarSet, QValueAxis
from PyQt5.QtGui import QPainter

from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtChart import QChart, QChartView, QHorizontalBarSeries, QBarSet, QValueAxis
from PyQt5.QtGui import QPainter

class LandingSiteTemperatureWidget(CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None, source_list=None, default_temperature=0):
        super().__init__(parent_widget)
     
        self.addSourceKey("payload_landing_site_temperature", float, Constants.payload_landing_site_temperature_key, default_value=0, hide_in_drop_down=True)
        
        self.temp = 10  # Initial temperature (replace this with your data fetching logic)
        self.bar_set = QBarSet(f"Temperature: {self.temp} °C")  # Initialize with a label showing the temp
        self.bar_set.append(self.temp)  # Set the initial temperature value
        self.bar_set.setColor(QColor(255, 0, 0))
        self.bar_set.labelFont().setPointSize(30)  # Set font size to 14 (adjust as needed)
        
        # Create a horizontal bar series and add the bar set
        self.series = QHorizontalBarSeries()
        self.series.append(self.bar_set)

        # Create a chart and add the series
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle("Payload Landing Site Temperature")
        title_font = QFont()
        title_font.setPointSize(20)
        self.chart.setTitleFont(title_font)
        self.label_font = QFont()
        self.label_font.setPointSize(18)  # Set the font size to 14 (adjust as needed)
        self.bar_set.setLabelFont(self.label_font)  # Apply the new font to the label
        self.chart.legend().setFont(self.label_font)

        # Create a value axis for the x-axis (horizontal axis)
        self.axis_x = QValueAxis()
        self.axis_x.setRange(0, 150)  # Set the range of the x-axis
        self.axis_x.setTickCount(4)   # Set the number of ticks (adjust as needed)
        self.axis_x.setTickInterval(50)  # Set the interval between ticks (adjust as needed)
        # Add the x-axis to the chart
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.series.attachAxis(self.axis_x)

        # Create a chart view to display the chart
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        # Set a background color to the chart view (example: light gray)
        self.chart_view.setStyleSheet("background-color: #f5f5f5; border: none;")  # Light gray background
        
        # Optionally, set the chart background to be transparent but keep the chart's title and other elements visible
        self.chart.setBackgroundBrush(Qt.transparent)  # Transparent background for the chart
        
        # Set the layout and add the chart view
        layout = QVBoxLayout(self)
        layout.addWidget(self.chart_view)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove any extra margins around the layout
        self.setLayout(layout)
        
        # Optionally, remove the widget's border as well
        self.setStyleSheet("border: none;")  # Removes the border from the widget itself
        
        self.resize(400, 200)  # Adjust size as needed

    def updateData(self, vehicle_data, updated_data):
        temp = self.getDictValueUsingSourceKey("payload_landing_site_temperature")
        self.bar_set.replace(0, temp)  # Replaces the first value in the bar set with the updated temp value
        self.bar_set.setLabel(f"Temperature: {temp} °C")  # Update the legend label with the current temperature value
        # Force a repaint to update the chart view
        self.chart_view.repaint()  # Forces a redraw (optional)
        self.chart_view.update()  # Another way to trigger a repaint
