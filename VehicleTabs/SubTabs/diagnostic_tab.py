"""
Code to define widget layout to drive warpauv
"""

from Widgets import TextBoxDropDownWidget

from VehicleTabs.SubTabs.sub_tab_common import SubTab


class DiagnosticTab(SubTab):
    def __init__(self):
        super().__init__()
        self.addWidget(TextBoxDropDownWidget.TextBoxDropDownWidget(self.mainWidget))

        self.canAddWidgets = True
