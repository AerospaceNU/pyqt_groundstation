"""
A rewrite of primary_tab to be more useful on a rocket
"""

from PyQt5.QtWidgets import QGridLayout, QSizePolicy

from Widgets import flight_display
from Widgets import vehicle_status_widget
from Widgets import video_widget
from Widgets import annunciator_panel
from Widgets import button_panel
from Widgets import simple_console_widget
from Widgets import map_widget

from MainTabs.main_tab_common import TabCommon


class RocketPrimaryTab(TabCommon):
    def __init__(self, mainWidget, vehicleName):
        super().__init__(mainWidget, vehicleName)

        self.FlightDisplay = self.addWidget(flight_display.FlightDisplay(compass_and_text=False))
        self.StatusBar = self.addWidget(vehicle_status_widget.VehicleStatusWidget())
        self.VideoPanel = self.addWidget(video_widget.VideoWidget())
        self.Annunciator = self.addWidget(annunciator_panel.AnnunciatorPanel())
        self.ButtonPanel = self.addWidget(button_panel.ButtonPanel())
        self.Console = self.addWidget(simple_console_widget.SimpleConsoleWidget())
        self.Map = self.addWidget(map_widget.MapWidget())

        self.ButtonPanel.clearMapButton.clicked.connect(self.Map.clearMap)  # This is a sketchy way to do this

        layout = QGridLayout()
        layout.addWidget(self.StatusBar, 1, 1, 1, 2)  # Upper right
        layout.addWidget(self.FlightDisplay, 1, 3, 2, 2)  # Upper Left
        layout.addWidget(self.VideoPanel, 2, 1, 3, 2)  # Lower Left
        layout.addWidget(self.Map, 2, 1, 3, 2)
        layout.addWidget(self.Annunciator, 3, 3, 1, 1)  # Lower right (but biased toward center)
        layout.addWidget(self.ButtonPanel, 3, 4, 1, 1)
        layout.addWidget(self.Console, 4, 3, 1, 2)

        layout.setRowStretch(1, 0)
        layout.setColumnStretch(1, 0)
        self.tabMainWidget.setLayout(layout)

    def customUpdate(self, data):
        self.ButtonPanel.setMaximumWidth(max(self.FlightDisplay.width() - self.Annunciator.width() - 6, 5))

        selectedVideo = self.ButtonPanel.getSelectedVideo()

        if selectedVideo == "Map":
            self.Map.show()
            self.VideoPanel.hide()
        else:
            self.Map.hide()
            self.VideoPanel.show()

        self.VideoPanel.setSource(selectedVideo)
