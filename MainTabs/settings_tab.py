"""
Code to define widget layout to drive warpauv
"""

from MainTabs.main_tab_common import TabCommon

from Widgets import control_station_status


class SettingsTab(TabCommon):
    def __init__(self, mainWidget, vehicleName):
        super().__init__(mainWidget, vehicleName)

        self.ControlStationData = self.addWidget(control_station_status.ControlStationStatus(self.tabMainWidget))
        self.ControlStationData.setMinimumSize(400, 150)

        self.addWidget(self.ControlStationData)
