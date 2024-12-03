from PyQt5.QtWidgets import QWidget, QVBoxLayout
from src.Widgets.QWidget_Parts import simple_bar_graph_widget
from src.Widgets.custom_q_widget_base import CustomQWidgetBase

class PayloadBatteryBarWidget(CustomQWidgetBase):
    def __init__(self, parent=None, default_battery_level=50):
        super().__init__(parent)
        self.BatteryStatus = simple_bar_graph_widget.SimpleBarGraphWidget(title="Battery", minValue=0, maxValue=100)

        layout = QVBoxLayout()
        layout.addWidget(self.BatteryStatus)
        
        self.setLayout(layout)
        self.setMinimumSize(100,200)

        # Set the default battery level
        self.update_battery_level(default_battery_level)

    def update_battery_level(self, battery_level):
        """Update the battery level in the SimpleBarGraphWidget."""
        self.BatteryStatus.setValue(battery_level)

    def set_default_value(self, battery_level):
        """Method to change the default value dynamically."""
        self.update_battery_level(battery_level)


