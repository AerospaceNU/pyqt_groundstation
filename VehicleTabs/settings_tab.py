"""
Code to define widget layout to drive warpauv
"""

from VehicleTabs.vehicle_tab_common import VehicleTabCommon

from Widgets import ControlStationStatus


class SettingsTab(VehicleTabCommon):
    def __init__(self, mainWidget, vehicleName):
        super().__init__(mainWidget, vehicleName)

        self.ControlStationData = self.addWidget(ControlStationStatus.ControlStationStatus(self.mainWidget))
        self.ControlStationData.setMinimumSize(400, 150)

        self.addWidget(self.ControlStationData)
