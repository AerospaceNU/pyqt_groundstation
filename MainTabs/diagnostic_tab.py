"""
Code to define widget layout to drive warpauv
"""

from Widgets import text_box_drop_down_widget

from MainTabs.main_tab_common import TabCommon


class DiagnosticTab(TabCommon):
    def __init__(self, mainWidget, vehicleName):
        super().__init__(mainWidget, vehicleName)
        self.addWidget(text_box_drop_down_widget.TextBoxDropDownWidget(self.tabMainWidget))

        self.canAddWidgets = True
