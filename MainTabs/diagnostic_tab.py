"""
Code to define widget layout to drive warpauv
"""

from Widgets import TextBoxDropDownWidget

from MainTabs.main_tab_common import TabCommon


class DiagnosticTab(TabCommon):
    def __init__(self, mainWidget, vehicleName):
        super().__init__(mainWidget, vehicleName)
        self.addWidget(TextBoxDropDownWidget.TextBoxDropDownWidget(self.tabMainWidget))

        self.canAddWidgets = True
