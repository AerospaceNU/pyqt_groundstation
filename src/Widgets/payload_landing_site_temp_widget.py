from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPainter
from PyQt5.QtChart import QChart, QChartView, QHorizontalBarSeries, QBarSet, QValueAxis
from src.Widgets.custom_q_widget_base import CustomQWidgetBase
from src.constants import Constants
import numpy as np
class DraggableHandle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.setFixedHeight(30)
        self.setStyleSheet("background-color: #d0d0d0; border-radius: 4px 4px 0 0;")
        # Variables to track dragging state
        self._dragging = False
        self._drag_start_position = None
       
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_start_position = event.globalPos() - self.parent_widget.pos()
            event.accept()
           
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self._dragging:
            self.parent_widget.move(event.globalPos() - self._drag_start_position)
            event.accept()
           
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = False
            event.accept()

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

        # Create the main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
       
        # Add a draggable handle at the top
        self.handle = DraggableHandle(self)
        main_layout.addWidget(self.handle)

        # Initialize temperature bar
        self.temp = 10
        self.bar_set = QBarSet(f"Temperature: {self.temp} °C")
        self.bar_set.append(self.temp)
        self.bar_set.setColor(QColor(255, 0, 0))

        # Apply font to bar label
        
        label_font = QFont()
        label_font.setPointSize(16)
        self.bar_set.setLabelFont(label_font)
    
        # Create horizontal bar series
        self.series = QHorizontalBarSeries()
        self.series.append(self.bar_set)

        # Create and configure chart
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle("Payload Landing Site Temperature")
        
        title_font = QFont("Arial", 17)
        title_font.setBold(True)  # This makes the title bold
        self.chart.setTitleFont(title_font)    
        self.chart.legend().setFont(label_font)
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
       
        # Add chart view to the main layout
        main_layout.addWidget(self.chart_view)
       
        # Set the main layout
        self.setLayout(main_layout)

        # Widget appearance
        self.setStyleSheet("border: 1px solid #a0a0a0; border-radius: 4px;")
        self.resize(400, 275)  # Add extra height for the handle

    def updateData(self, vehicle_data, updated_data):
        # Update temperature value and label
        temp = self.getDictValueUsingSourceKey("payload_landing_site_temperature")
        self.bar_set.replace(0, temp)
        self.bar_set.setLabel(f"Temperature: {temp} °C")
        self.chart_view.update()
