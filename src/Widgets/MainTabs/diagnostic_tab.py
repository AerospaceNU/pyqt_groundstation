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
from src.Widgets.payload_landing_site_temp_widget import LandingSiteTemperatureWidget
from src.Widgets.payload_battery_widget import PayloadBatteryWidget
from src.Modules.random_data_interface import RandomDataInterface
from src.Widgets.payload_apogee_reached_widget import PayloadApogeeAltitudeWidget
from src.Widgets.payload_maximum_velocity_reached_widget import PayloadMaximumVelocity

class DiagnosticTab(TabCommon):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        self.addWidget(LandingSiteTemperatureWidget(self))
        self.addWidget(PayloadMaximumVelocity(self))
        self.addWidget(PayloadApogeeAltitudeWidget(self)).move(800, 400)
        self.addWidget(PayloadBatteryWidget(self)).move(750, 400)
        self.addWidget(diagnostics_widget.DiagnosticsWidget(self))
        self.addWidget(diagnostics_widget.DiagnosticsWidget(self))
        self.addWidget(simple_console_widget.SimpleConsoleWidget(self))
        self.addWidget(reconfigure_widget.ReconfigureWidget(self))
        self.addWidget(pyro_display_widget.PyroWidget(self))
        self.addWidget(qr_code_widget.RocketLocationQrCode(self)).move(0, 400)
        self.addWidget(CompleteConsoleWidget(self)).move(0, 200)
        
        layout = QGridLayout()
        layout.setRowStretch(1,0)
        layout.setColumnStretch(1,0)
        self.setLayout(layout)
       