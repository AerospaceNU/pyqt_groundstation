"""
Settings tab.  Pretty useless right now
"""

from MainTabs.main_tab_common import TabCommon

from Widgets import control_station_status


class SettingsTab(TabCommon):
    def __init__(self, vehicleName):
        super().__init__(vehicleName)

        self.ControlStationData = self.addWidget(control_station_status.ControlStationStatus(self))
        self.ControlStationData.setMinimumSize(400, 150)

        self.addWidget(self.ControlStationData)
