from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.Widgets.custom_q_widget_base import CustomQWidgetBase
from src.constants import Constants

class DraggableHandle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.setFixedHeight(30)
        self.setStyleSheet("background-color: #d0d0d0; border-radius: 4px 4px 0 0;")
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

class CrewSurvivabilityWidget(CustomQWidgetBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.addSourceKey(
            "payload_crew_survivabilty",
            float,
            Constants.payload_crew_survivability_key,
            hide_in_drop_down=True
        )

        self.chart = QChart()
        self.series = QPieSeries()
        self.chart.addSeries(self.series)
        self.chart.setTitle("Crew Survivability")
        title_font = QFont("Arial", 17)
        title_font.setBold(True)  # This makes the title bold
        self.chart.setTitleFont(title_font)
        self.chart.setBackgroundBrush(Qt.transparent)
        self.chartview = QChartView(self.chart)
        self.chartview.setStyleSheet("background-color: #f5f5f5; border: none;")

        # Legend setup
        legend = self.chart.legend()
        legend.setVisible(True)
        legend.setAlignment(Qt.AlignBottom)
        legend.setMarkerShape(legend.MarkerShapeCircle)
        legend.setFont(QFont("Arial", 14))
    
        # Layouts
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Draggable handle
        self.handle = DraggableHandle(self)
        main_layout.addWidget(self.handle)

        # Chart content
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(self.chartview)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

        # Appearance
        self.setMinimumSize(375, 300)
        self.setStyleSheet("border: 1px solid #a0a0a0; border-radius: 4px;")

    def updateChart(self, survivability):
        survivability = float(survivability) if survivability is not None else 0.0
        risk = 100 - survivability

        if len(self.series.slices()) == 0:
            self.series.append(f'Survivability: {survivability:.1f}%', survivability)
            self.series.append(f'Risk: {risk:.1f}%', risk)
        else:
            slices = self.series.slices()
            slices[0].setValue(survivability)
            slices[0].setLabel(f'Survivability: {survivability:.1f}%')
            slices[1].setValue(risk)
            slices[1].setLabel(f'Risk: {risk:.1f}%')

    def updateData(self, vehicle_data, updated_data):
        survivability = self.getDictValueUsingSourceKey("payload_crew_survivabilty")
        self.updateChart(survivability)
