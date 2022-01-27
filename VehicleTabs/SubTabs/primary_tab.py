"""
Code to define widget layout to drive warpauv
"""

from PyQt5.QtWidgets import QGridLayout

from Widgets import FlightDisplay
from Widgets import VehicleStatusWidget
from Widgets import VideoWidget
from Widgets import ControlStationStatus
from Widgets import AnnunciatorPanel
from Widgets import ButtonPanel
from Widgets import SimpleConsoleWidget
from Widgets import MapWidget

from VehicleTabs.SubTabs.sub_tab_common import SubTab


class PrimaryTab(SubTab):
    def __init__(self):
        super().__init__()

        self.FlightDisplay = self.addWidget(FlightDisplay.FlightDisplay())
        self.StatusBar = self.addWidget(VehicleStatusWidget.VehicleStatusWidget())
        self.VideoPanel = self.addWidget(VideoWidget.VideoWidget())
        self.Annunciator = self.addWidget(AnnunciatorPanel.AnnunciatorPanel())
        self.ButtonPanel = self.addWidget(ButtonPanel.ButtonPanel())
        self.Console = self.addWidget(SimpleConsoleWidget.SimpleConsoleWidget())
        self.Map = self.addWidget(MapWidget.MapWidget())

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
        self.mainWidget.setLayout(layout)

    def update(self):
        self.ButtonPanel.setMaximumWidth(max(self.FlightDisplay.width() - self.Annunciator.width() - 6, 5))

        selectedVideo = self.ButtonPanel.getSelectedVideo()

        if selectedVideo == "Map":
            self.Map.show()
            self.VideoPanel.hide()
        else:
            self.Map.hide()
            self.VideoPanel.show()

        self.VideoPanel.setSource(selectedVideo)
