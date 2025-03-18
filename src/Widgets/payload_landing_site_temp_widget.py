from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from src.Widgets.custom_q_widget_base import CustomQWidgetBase
from src.constants import Constants
from src.Widgets.QWidget_Parts import simple_bar_graph_widget
from PyQt5.QtWidgets import QGridLayout, QLabel
from PyQt5.QtGui import QFont
class LandingSiteTemperatureWidget(CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None, source_list=None, default_temperature=0):
        super().__init__(parent_widget)

        # self.draggable = True  

        # self.title_label = QLabel("Payload Landing Site Temperature")
        # self.title_label.setWordWrap(True)
        # self.title_label.setAlignment(Qt.AlignCenter)
        
        self.payload_temp_graph = simple_bar_graph_widget.SimpleBarGraphWidget(
            title="Payload Landing \n Temp", minValue=0, maxValue=500, barColor="rgb(255, 0, 0)"
        )
        
        
        vbox = QGridLayout(self)
        vbox.addWidget(self.payload_temp_graph)  
        vbox.setSpacing(5)
        vbox.setContentsMargins(10, 10, 10, 10)  # Adds 10px margin at the bottom of the title

        # vbox.setContentsMargins(0,0,0,0)
        # vbox.addWidget(self.toggle_button, alignment=Qt.AlignCenter)  # Uncomment if using toggle button
        self.setLayout(vbox)

        # self.resize(100, 1000)  
        self.addSourceKey("payload_landing_site_temperature", float, Constants.payload_landing_site_temperature_key, default_value=0, hide_in_drop_down=True)
        # self.setMinimumSize(100,200)
        
        # font = QFont()
        # font.setPointSize(6)
        
        # #vbox.setfont(font)
        # self.setFont(font)

    def updateData(self, vehicle_data, updated_data):
        """Update temperature value if enabled."""
        temp = self.getDictValueUsingSourceKey("payload_landing_site_temperature")
        self.payload_temp_graph.setValue(temp)
        
    def adjustSize(self) -> None:
        self.resize(100, 250)
