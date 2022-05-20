"""
Settings tab.  Pretty useless right now
"""

from MainTabs.main_tab_common import TabCommon

from Widgets import control_station_status
from Widgets.local_sim_widget import LocalSimWidget
from Widgets import board_usb_offloader_widget


class SettingsTab(TabCommon):
    def __init__(self, tab_name, parent=None):
        super().__init__(tab_name, parent=parent)

        self.ControlStationData = self.addWidget(control_station_status.ControlStationStatus(self))
        self.ControlStationData.setMinimumSize(400, 150)

        self.addWidget(LocalSimWidget(self))
        self.addWidget(board_usb_offloader_widget.BoardCliWrapper(self))

        self.widgetList[1].move(600, 0)
