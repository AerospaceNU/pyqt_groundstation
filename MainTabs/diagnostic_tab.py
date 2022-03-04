"""
Code to define widget layout to drive warpauv
"""

from Widgets import text_box_drop_down_widget
from Widgets import simple_console_widget

from MainTabs.main_tab_common import TabCommon


class DiagnosticTab(TabCommon):
    def __init__(self, mainWidget, vehicleName):
        super().__init__(mainWidget, vehicleName)
        self.addWidget(text_box_drop_down_widget.TextBoxDropDownWidget(self.tabMainWidget))
        self.addWidget(text_box_drop_down_widget.TextBoxDropDownWidget(self.tabMainWidget))
        self.addWidget(simple_console_widget.SimpleConsoleWidget(self.tabMainWidget))

        self.widgetList[1].move(400, 0)  # Move the widgets to better spots
        self.widgetList[2].move(1000, 0)  # This isn't really the best way to reference the object, but I don't care

        self.canAddWidgets = True
