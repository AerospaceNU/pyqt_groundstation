"""
Settings tab.  Pretty useless right now
"""

from src.Widgets.MainTabs.main_tab_common import TabCommon
from src.Widgets import control_station_status
from src.Widgets.local_sim_widget import LocalSimWidget


class SettingsTab(TabCommon):
    def __init__(self,  parent=None):
        super().__init__( parent=parent)

        self.ControlStationData = self.addWidget(control_station_status.ControlStationStatus(self))
        self.ControlStationData.setMinimumSize(400, 150)

        self.addWidget(LocalSimWidget(self))

        self.widgetList[1].move(600, 0)
