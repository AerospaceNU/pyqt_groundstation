"""
Code to define widget layout to drive warpauv
"""

from VehicleTabs.vehicle_tab_common import VehicleTabCommon


class WarpAUVTab(VehicleTabCommon):
    """Where the specific layout of widgets for warpauv is defined"""

    def __init__(self, mainWidget, vehicleName):
        super().__init__(mainWidget, vehicleName)

        self.addSubTab("Primary", "primary")
        self.addSubTab("Diagnostic", "diagnostic")
        self.addSubTab("Misc")
