"""
A rewrite of primary_tab to be more useful on a rocket
"""

from PyQt5.QtWidgets import QGridLayout, QSizePolicy
from src.Widgets.prop_control_widget import PropControlWidget

from src.constants import Constants
from src.Widgets.MainTabs.main_tab_common import TabCommon
from src.Widgets import (
    annunciator_panel,
    button_panel,
    flight_display,
    graph_widget,
    map_widget,
    simple_console_widget,
    vehicle_status_widget,
    video_widget,
)


class RocketPrimaryTab(TabCommon):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.FlightDisplay = self.addWidget(flight_display.FlightDisplay(compass_and_text=False, use_navball_widget=False))
        self.StatusBar = self.addWidget(vehicle_status_widget.VehicleStatusWidget())
        self.VideoPanel = self.addWidget(video_widget.VideoWidget())
        self.Annunciator = self.addWidget(annunciator_panel.AnnunciatorPanel())
        self.ButtonPanel = self.addWidget(button_panel.ButtonPanel())
        self.Console = self.addWidget(simple_console_widget.SimpleConsoleWidget())
        self.Map = self.addWidget(map_widget.MapWidget())
        self.AltitudeGraph = self.addWidget(graph_widget.GraphWidget(title="Altitude", source_list=[Constants.altitude_key]))

        self.ButtonPanel.clearMapButton.clicked.connect(self.Map.clearMap)
        self.ButtonPanel.resetDatumButton.clicked.connect(self.Map.resetDatum)
        self.ButtonPanel.resetGraphButton.clicked.connect(self.AltitudeGraph.clearGraph)
        self.ButtonPanel.resetOriginButton.clicked.connect(self.Map.resetOrigin)

        layout = QGridLayout()
        layout.addWidget(self.StatusBar, 1, 1, 1, 2)  # Upper right
        layout.addWidget(self.FlightDisplay, 1, 3, 2, 2)  # Upper Left
        layout.addWidget(self.AltitudeGraph, 3, 3, 1, 2)
        layout.addWidget(self.VideoPanel, 2, 1, 4, 2)  # Lower Left
        layout.addWidget(self.Map, 2, 1, 4, 2)
        layout.addWidget(self.Annunciator, 4, 3, 1, 1)  # Lower right (but biased toward center)
        layout.addWidget(self.ButtonPanel, 4, 4, 1, 1)
        layout.addWidget(self.Console, 5, 3, 1, 2)

        self.AltitudeGraph.setMaximumHeight(350)
        layout.setRowStretch(1, 0)
        layout.setColumnStretch(1, 0)
        self.setLayout(layout)

        self.ButtonPanel.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.Console.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

    def customUpdateVehicleData(self, data):
        selectedVideo = self.ButtonPanel.getSelectedVideo()

        if selectedVideo == "Map":
            self.Map.show()
            self.VideoPanel.hide()
        else:
            self.Map.hide()
            self.VideoPanel.show()

        self.VideoPanel.setSource(selectedVideo)
