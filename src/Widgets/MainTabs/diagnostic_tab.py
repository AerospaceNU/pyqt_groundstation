from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy, QScrollArea
from src.Widgets import (
    diagnostics_widget,
    pyro_display_widget,
    qr_code_widget,
    reconfigure_widget,
    simple_console_widget,
)

from PyQt5.QtWidgets import QGridLayout 

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
        
        # Main layout for the tab
        main_layout = QVBoxLayout(self)

        # Create a horizontal layout for the headers
        header_layout = QHBoxLayout()

        # Create FCB header and align it to the left
        fcb_header = QLabel("\n                                     FCB                                                                                              PAYLOAD")
        fcb_header.setStyleSheet("font-weight: bold; font-size: 30px;")
        
        # Add FCB header to the layout with stretch factor 1 (left)
        header_layout.addWidget(fcb_header)

        # Add header_layout to the main_layout
        main_layout.addLayout(header_layout)

        # Scrollable area for content
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        
        self.scroll_widget = QWidget()
        self.scroll_widget.setFixedSize(2000, 2000)  # Adjust this size to ensure scrollability
        self.scroll_area.setWidget(self.scroll_widget)

        layout = QGridLayout(self.scroll_widget)
        layout.setRowStretch(1, 0)
        layout.setColumnStretch(1, 0)

        self.addWidget(pyro_display_widget.PyroWidget(self.scroll_widget)).move(50, 50)
        self.addWidget(qr_code_widget.RocketLocationQrCode(self.scroll_widget)).move(50, 200)
        self.addWidget(CompleteConsoleWidget(self.scroll_widget)).move(420, 200) # go back
        self.addWidget(reconfigure_widget.ReconfigureWidget(self.scroll_widget)).move(420, 400)
        self.addWidget(diagnostics_widget.DiagnosticsWidget(self.scroll_widget)).move(420, 620)
        self.addWidget(simple_console_widget.SimpleConsoleWidget(self.scroll_widget)).move(50, 750)
        self.addWidget(PayloadDataTransmissionButton(self.scroll_widget, arduino_interface=ArduinoDataInterface())).move(800, 50)
        self.addWidget(PayloadUserInputWidget(self.scroll_widget, arduino_interface=ArduinoDataInterface())).move(1090, 50)
        self.addWidget(PayloadLandingTimeWidget(self.scroll_widget)).move(800, 280)
        self.addWidget(PayloadApogeeAltitudeWidget(self.scroll_widget)).move(1050, 240)
        self.addWidget(PayloadBatteryWidget(self.scroll_widget)).move(1320, 240) #between 90 and 130, V*10
        self.addWidget(PayloadLandingVelocity(self.scroll_widget)).move(800, 500)
        self.addWidget(LandingSiteTemperatureWidget(self.scroll_widget)).move(1080, 470) #convert kelvin to celsius  #RANGE??????
        self.addWidget(PayloadMaximumVelocity(self.scroll_widget)).move(800, 750)
        self.addWidget(PayloadOrientationWidget(self.scroll_widget)).move(1100, 780)
        self.addWidget(CrewSurvivabilityWidget(self.scroll_widget)).move(900, 1000)

        # Add the scroll area to the main layout
        main_layout.addWidget(self.scroll_area)

        # Set the layout for the tab
        self.setLayout(main_layout)


