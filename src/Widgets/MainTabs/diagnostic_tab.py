from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QScrollArea
from src.Widgets import (
    diagnostics_widget,
    pyro_display_widget,
    qr_code_widget,
    reconfigure_widget,
    simple_console_widget,
)

from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

from src.Widgets.complete_console_widget import CompleteConsoleWidget
from src.Widgets.MainTabs.main_tab_common import TabCommon
from src.Widgets.payload_landing_site_temp_widget import LandingSiteTemperatureWidget
from src.Widgets.payload_battery_widget import PayloadBatteryWidget
from src.Modules.random_data_interface import RandomDataInterface
from src.Widgets.payload_landing_time import PayloadLandingTimeWidget
from src.Widgets.payload_apogee_reached_widget import PayloadApogeeAltitudeWidget
from src.Widgets.payload_maximum_velocity_reached_widget import PayloadMaximumVelocity
from src.Widgets.payload_landing_velocity_widget import PayloadLandingVelocity
from src.Widgets.payload_crew_survivabilty_widget import CrewSurvivabilityWidget
from src.Widgets.payload_data_transmission_button import PayloadDataTransmissionButton
from src.Modules.arduino_random_data_interface import ArduinoDataInterface
from src.Widgets.payload_orientation_widget import PayloadOrientationWidget
from src.Widgets.payload_send_message_box import PayloadUserInputWidget

class DiagnosticTab(TabCommon):
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        
        self.scroll_widget = QWidget()
        self.scroll_widget.setFixedSize(2000, 2000) # Adjust this size to ensure scrollability
        self.scroll_area.setWidget(self.scroll_widget)

        layout = QGridLayout(self.scroll_widget)
        layout.setRowStretch(1, 0)
        layout.setColumnStretch(1, 0)
        self.addWidget(diagnostics_widget.DiagnosticsWidget(self.scroll_widget))
        self.addWidget(diagnostics_widget.DiagnosticsWidget(self.scroll_widget))
        self.addWidget(simple_console_widget.SimpleConsoleWidget(self.scroll_widget))
        self.addWidget(reconfigure_widget.ReconfigureWidget(self.scroll_widget)).move(0,1200) # the big one with a lot of dara
        self.addWidget(pyro_display_widget.PyroWidget(self.scroll_widget))
        self.addWidget(qr_code_widget.RocketLocationQrCode(self.scroll_widget)).move(0, 400)
        

        self.addWidget(PayloadDataTransmissionButton(self.scroll_widget, arduino_interface=ArduinoDataInterface())).move(700, 50)
        self.addWidget(PayloadUserInputWidget(self.scroll_widget, arduino_interface=ArduinoDataInterface())).move(950,50)
        self.addWidget(PayloadLandingTimeWidget(self.scroll_widget)).move(700, 300)
        self.addWidget(PayloadApogeeAltitudeWidget(self.scroll_widget)).move(950, 250)
        self.addWidget(PayloadBatteryWidget(self.scroll_widget)).move(1150, 300)

        self.addWidget(LandingSiteTemperatureWidget(self.scroll_widget)).move(1000, 200)
        self.addWidget(CompleteConsoleWidget(self.scroll_widget)).move(0, 200)
        self.addWidget(CrewSurvivabilityWidget(self.scroll_widget)).move(1100, 400)
        self.addWidget(PayloadMaximumVelocity(self.scroll_widget)).move(900, 400)
        self.addWidget(PayloadLandingVelocity(self.scroll_widget)).move(850, 400)
        self.addWidget(PayloadOrientationWidget(self.scroll_widget))

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)