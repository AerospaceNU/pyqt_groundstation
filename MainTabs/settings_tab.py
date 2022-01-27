"""
Code to define widget layout to drive warpauv
"""

from MainTabs.main_tab_common import TabCommon

from Widgets import ControlStationStatus


class SettingsTab(TabCommon):
    def __init__(self, mainWidget, vehicleName):
        super().__init__(mainWidget, vehicleName)

        self.ControlStationData = self.addWidget(ControlStationStatus.ControlStationStatus(self.tabMainWidget))
        self.ControlStationData.setMinimumSize(400, 150)

        self.addWidget(self.ControlStationData)
