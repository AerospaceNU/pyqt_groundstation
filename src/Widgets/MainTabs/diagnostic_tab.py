from PyQt5.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from src.Modules.arduino_data_interface import ArduinoDataInterface
from src.Modules.random_data_interface import RandomDataInterface
from src.Widgets import (
    diagnostics_widget,
    pyro_display_widget,
    qr_code_widget,
    reconfigure_widget,
    simple_console_widget,
)
from src.Widgets.complete_console_widget import CompleteConsoleWidget
from src.Widgets.MainTabs.main_tab_common import TabCommon
from src.Widgets.payload_acceleration_widget import PayloadAccelerationWidget
from src.Widgets.payload_apogee_reached_widget import PayloadApogeeAltitudeWidget
from src.Widgets.payload_battery_widget import PayloadBatteryWidget
from src.Widgets.payload_crew_survivabilty_widget import CrewSurvivabilityWidget
from src.Widgets.payload_data_transmission_button import PayloadDataTransmissionButton
from src.Widgets.payload_landing_site_temp_widget import LandingSiteTemperatureWidget
from src.Widgets.payload_landing_time import PayloadLandingTimeWidget
from src.Widgets.payload_landing_velocity_widget import PayloadLandingVelocity
from src.Widgets.payload_maximum_velocity_reached_widget import PayloadMaximumVelocity
from src.Widgets.payload_orientation_widget import PayloadOrientationWidget
from src.Widgets.payload_run_time_widget import PayloadRunTimeWidget
from src.Widgets.payload_send_message_box import PayloadUserInputWidget


class DiagnosticTab(TabCommon):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        print("diag happen ")
        adi = ArduinoDataInterface(is_connected=False)

        # Main layout for the tab
        main_layout = QVBoxLayout(self)

        # Create a horizontal layout for the headers
        header_layout = QHBoxLayout()

        # Create FCB header and align it to the left
        fcb_header = QLabel("                                     FCB                                                                                              PAYLOAD")
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

        self.addWidget(qr_code_widget.RocketLocationQrCode(self.scroll_widget)).move(50, 50)
        self.addWidget(pyro_display_widget.PyroWidget(self.scroll_widget)).move(50, 625)
        self.addWidget(CompleteConsoleWidget(self.scroll_widget)).move(520, 50)  # go back
        self.addWidget(reconfigure_widget.ReconfigureWidget(self.scroll_widget)).move(520, 215)
        self.addWidget(diagnostics_widget.DiagnosticsWidget(self.scroll_widget)).move(520, 400)
        self.addWidget(simple_console_widget.SimpleConsoleWidget(self.scroll_widget)).move(50, 950)
        self.addWidget(PayloadDataTransmissionButton(self.scroll_widget, arduino_interface=adi)).move(875, 50)
        self.addWidget(PayloadUserInputWidget(self.scroll_widget, arduino_interface=adi)).move(875, 175)
        self.addWidget(PayloadBatteryWidget(self.scroll_widget)).move(1200, 125)  # between 90 and 130, V*10
        self.addWidget(PayloadRunTimeWidget(self.scroll_widget)).move(1350, 125)
        self.addWidget(PayloadLandingTimeWidget(self.scroll_widget)).move(1600, 125)
        self.addWidget(PayloadMaximumVelocity(self.scroll_widget)).move(875, 350)
        self.addWidget(PayloadLandingVelocity(self.scroll_widget)).move(1090, 350)
        self.addWidget(PayloadAccelerationWidget(self.scroll_widget)).move(1305, 350)
        self.addWidget(PayloadApogeeAltitudeWidget(self.scroll_widget)).move(1490, 350)
        self.addWidget(PayloadOrientationWidget(self.scroll_widget)).move(1675, 350)
        self.addWidget(LandingSiteTemperatureWidget(self.scroll_widget)).move(875, 550)  # convert kelvin to celsius  #RANGE??????
        self.addWidget(CrewSurvivabilityWidget(self.scroll_widget)).move(1400, 550)

        # Add the scroll area to the main layout
        main_layout.addWidget(self.scroll_area)

        # Set the layout for the tab
        self.setLayout(main_layout)
