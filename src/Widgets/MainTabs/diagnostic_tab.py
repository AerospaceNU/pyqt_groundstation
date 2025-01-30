from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout
from src.Widgets import (
    diagnostics_widget,
    pyro_display_widget,
    qr_code_widget,
    reconfigure_widget,
    simple_console_widget,
)
from src.Widgets.complete_console_widget import CompleteConsoleWidget
from src.Widgets.MainTabs.main_tab_common import TabCommon
from src.Widgets.payload_temperature_widget import PayloadTemperatureWidget
from src.Widgets.payload_battery_widget import PayloadBatteryBarWidget
from src.Modules.random_data_interface import RandomDataInterface

class DiagnosticTab(TabCommon):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        self.Temperature = self.addWidget(PayloadTemperatureWidget())
        self.addWidget(diagnostics_widget.DiagnosticsWidget(self))
        self.addWidget(diagnostics_widget.DiagnosticsWidget(self))
        self.addWidget(simple_console_widget.SimpleConsoleWidget(self))
        self.addWidget(reconfigure_widget.ReconfigureWidget(self))
        self.addWidget(pyro_display_widget.PyroWidget(self))
        self.addWidget(qr_code_widget.RocketLocationQrCode(self)).move(0, 400)
        self.addWidget(CompleteConsoleWidget(self)).move(0, 200)
        
        layout = QGridLayout()
        layout.addWidget(self.Temperature, 2, 1, 4, 2)
        layout.setRowStretch(1,0)
        layout.setColumnStretch(1,0)
        self.setLayout(layout)
       