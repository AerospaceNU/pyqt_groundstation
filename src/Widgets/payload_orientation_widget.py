from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from src.Widgets.custom_q_widget_base import CustomQWidgetBase
from src.constants import Constants
from src.Widgets.QWidget_Parts import simple_bar_graph_widget
from PyQt5.QtWidgets import QGridLayout, QLabel

class PayloadOrientationWidget(CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None, source_list=None, default_temperature=0):
        super().__init__(parent_widget)

        self.orientation_label = QLabel("Orientation", self)
        self.orientation_label.setAlignment(Qt.AlignCenter)

        vbox = QVBoxLayout()
        vbox.addWidget(self.orientation_label)
        self.setLayout(vbox)

        self.title = "Payload Orientation (°)"
        self.addSourceKey("payload_orientation", float, Constants.payload_orientation_key, default_value=False, hide_in_drop_down=True)
    
    def updateData(self, vehicle_data, updated_data):
        payload_orientation = self.getDictValueUsingSourceKey("payload_orientation")
        self.orientation_label.setText(f"Payload Orientation (°) (\n \n \n {payload_orientation} m")

    def adjustSize(self) -> None:
        self.resize(250, 200)    
    