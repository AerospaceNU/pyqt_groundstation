"""
Doesn't do anything by itself, but tabs that hold other tabs should extend this one
"""

from src.Widgets.MainTabs.main_tab_common import TabCommon
from src.Widgets import custom_q_widget_base


class SubTabHolder(TabCommon):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.subTabObjects = []

    def addSubTab(self, tab_name: str, tab_object: TabCommon):
        self.subTabObjects.append(tab_object)

    def getActiveTab(self) -> TabCommon:
        """Override this """
        return None

    def updateVehicleData(self, data, console_data, updated_data, recorded_data):
        """Just calls the update function for the sub tabs"""
        if isinstance(data, dict):
            vehicle_data = data
        else:
            vehicle_data = {}

        if not isinstance(updated_data, dict):
            updated_data = {}

        callbacks = []

        for tab in self.subTabObjects:
            callbacks += tab.updateVehicleData(vehicle_data, console_data, updated_data, recorded_data)

        self.customUpdateVehicleData(data)
        self.update()
        return callbacks

    def addWidget(self, widget: custom_q_widget_base.CustomQWidgetBase, widget_name=None) -> custom_q_widget_base.CustomQWidgetBase:
        active_tab_object = self.getActiveTab()

        if active_tab_object is not None:
            return active_tab_object.addWidget(widget, widget_name)
        else:
            return None
