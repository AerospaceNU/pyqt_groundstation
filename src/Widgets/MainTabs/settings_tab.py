"""
Settings tab.  Pretty useless right now
"""

from src.Widgets import control_station_status
from src.Widgets.local_sim_widget import LocalSimWidget
from src.Widgets.logger_control_widget import LoggerControlWidget
from src.Widgets.MainTabs.main_tab_common import TabCommon


class SettingsTab(TabCommon):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.ControlStationData = self.addWidget(control_station_status.ControlStationStatus(self))
        self.ControlStationData.setMinimumSize(400, 150)

        self.addWidget(LocalSimWidget(self))
        self.addWidget(LoggerControlWidget(self))

        self.widgetList[1].move(600, 0)
        self.widgetList[2].move(0, 300)
