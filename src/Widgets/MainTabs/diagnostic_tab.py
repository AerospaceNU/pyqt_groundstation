"""
Blank tab with diagnostic boxes
"""
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QWidget, QGridLayout, QSizePolicy
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


class DiagnosticTab(TabCommon):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        container_widget = QWidget(self)
        main_layout = QVBoxLayout(container_widget)

        not_payload_header = QLabel("Not Payload", self)
        not_payload_header.setStyleSheet("font-size: 20px; font-weight: bold;")
        main_layout.addWidget(not_payload_header)

        not_payload_layout = QGridLayout()  

        self.add_sectioned_widget(diagnostics_widget.DiagnosticsWidget(self), not_payload_layout, 0, 2)
        self.add_sectioned_widget(diagnostics_widget.DiagnosticsWidget(self), not_payload_layout, 1,2)
        self.add_sectioned_widget(simple_console_widget.SimpleConsoleWidget(self), not_payload_layout, 0, 1)
        self.add_sectioned_widget(reconfigure_widget.ReconfigureWidget(self), not_payload_layout, 1, 1)
        self.add_sectioned_widget(pyro_display_widget.PyroWidget(self), not_payload_layout, 0, 0)
        self.add_sectioned_widget(qr_code_widget.RocketLocationQrCode(self), not_payload_layout, 1, 0)
        self.add_sectioned_widget(CompleteConsoleWidget(self), not_payload_layout, 0, 0)

        main_layout.addLayout(not_payload_layout)

        payload_header = QLabel("Payload", self)
        payload_header.setStyleSheet("font-size: 20px; font-weight: bold;")
        main_layout.addWidget(payload_header)

        payload_layout = QGridLayout()  
        self.payload_temp_widget = PayloadTemperatureWidget(self)
        self.add_sectioned_widget(self.payload_temp_widget, payload_layout, 0, 0)
        self.payload_battery_widget = PayloadBatteryBarWidget(self)
        self.add_sectioned_widget(self.payload_battery_widget, payload_layout, 0, 4)
        main_layout.addLayout(payload_layout)
        self.setLayout(main_layout)
        self.canAddWidgets = True

    def update_temperature(self, temp):
        if hasattr(self, 'temp_meter_widget'):
            self.temp_meter_widget.update_temperature(temp)
