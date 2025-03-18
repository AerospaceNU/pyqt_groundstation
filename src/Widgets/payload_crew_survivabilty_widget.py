# from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
# from PyQt5.QtChart import QChart, QChartView, QPieSeries
# from src.Widgets.custom_q_widget_base import CustomQWidgetBase
# from src.constants import Constants

# class CrewSurvivabilityWidget(CustomQWidgetBase):
#     def __init__(self, parent=None):
#         super().__init__(parent)
        
#         self.chart = QChart()
#         self.series = QPieSeries()
        
#         self.chart.addSeries(self.series)
#         self.chart.setTitle("Crew Survivability")
#         self.chartview = QChartView(self.chart)
        
#         # Set the chart to use its built-in legend
#         self.chart.legend().setVisible(True)
        
#         layout = QHBoxLayout()
#         layout.addWidget(self.chartview)
        
#         # Adjust layout margins to make room for the chart
#         layout.setContentsMargins(0, 0, 0, 0)  # No space for extra widgets
#         layout.setSpacing(0)  # Minimize space between chart and the edge
        
#         self.setLayout(layout)
        
#         # Set a larger minimum size for the widget to accommodate both chart and legend
#         self.setMinimumSize(500, 300)
        
#         self.addSourceKey("payload_crew_survivabilty", float, Constants.payload_crew_survivability_key, hide_in_drop_down=True)
#         self.label = ""
        
#     def updateChart(self, survivability):
#         # Check if slices exist, then update them
#         if len(self.series.slices()) == 0:
#             self.series.append('survivability:' + str(survivability), survivability)
#             self.series.append('risk: ' + str(100 - survivability), 100 - survivability)
#         else:
#             self.series.slices()[0].setValue(survivability)
#             self.series.slices()[1].setValue(100 - survivability)

#     def updateData(self, vehicle_data, updated_data):
#         survivability = self.getDictValueUsingSourceKey("payload_crew_survivabilty")
#         self.updateChart(survivability)
        

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtCore import Qt  # Import Qt for alignment
from src.Widgets.custom_q_widget_base import CustomQWidgetBase
from src.constants import Constants

class CrewSurvivabilityWidget(CustomQWidgetBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.chart = QChart()
        self.series = QPieSeries()
        
        self.chart.addSeries(self.series)
        self.chart.setTitle("Crew Survivability")
        self.chartview = QChartView(self.chart)
        
        # Enable and align the legend
        legend = self.chart.legend()
        legend.setVisible(True)
        legend.setAlignment(Qt.AlignBottom)  # Adjust legend position
        legend.setMarkerShape(legend.MarkerShapeCircle)  # Optional customization
        legend.setFont(self.font())  # Use widget's default font
        
        layout = QHBoxLayout()
        layout.addWidget(self.chartview)
        
        # Adjust layout margins to make room for the chart
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.setLayout(layout)
        
        # Set a larger minimum size for the widget to accommodate both chart and legend
        self.setMinimumSize(500, 300)
        
        self.addSourceKey("payload_crew_survivabilty", float, Constants.payload_crew_survivability_key, hide_in_drop_down=True)
        self.label = ""
        
    def updateChart(self, survivability):
        # Ensure survivability is a valid number
        survivability = float(survivability) if survivability is not None else 0.0
        risk = 100 - survivability

        # Check if slices exist, then update them
        if len(self.series.slices()) == 0:
            self.series.append(f'Survivability: {survivability:.1f}%', survivability)
            self.series.append(f'Risk: {risk:.1f}%', risk)
        else:
            slices = self.series.slices()
            slices[0].setValue(survivability)
            slices[0].setLabel(f'Survivability: {survivability:.1f}%')  # Explicitly update label
            slices[1].setValue(risk)
            slices[1].setLabel(f'Risk: {risk:.1f}%')  # Explicitly update label

        
        
        
    # def updateChart(self, survivability):
    #     # Check if slices exist, then update them
    #     if len(self.series.slices()) == 0:
    #         self.series.append('Survivability: ' + str(survivability), survivability)
    #         self.series.append('Risk: ' + str(100 - survivability), 100 - survivability)
    #     else:
    #         self.series.slices()[0].setValue(survivability)
    #         self.series.slices()[1].setValue(100 - survivability)

    def updateData(self, vehicle_data, updated_data):
        survivability = self.getDictValueUsingSourceKey("payload_crew_survivabilty")
        self.updateChart(survivability)
