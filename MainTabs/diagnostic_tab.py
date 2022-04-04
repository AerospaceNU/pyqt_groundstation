"""
Blank tab with diagnostic boxes
"""

from Widgets import pyro_display_widget
from Widgets import text_box_drop_down_widget
from Widgets import simple_console_widget
from Widgets import reconfigure_widget
from Widgets import complete_console_widget
from Widgets.local_sim_widget import LocalSimWidget

from MainTabs.main_tab_common import TabCommon


class DiagnosticTab(TabCommon):
    def __init__(self, tab_name):
        super().__init__(tab_name)
        self.addWidget(text_box_drop_down_widget.TextBoxDropDownWidget(self))
        self.addWidget(text_box_drop_down_widget.TextBoxDropDownWidget(self))
        self.addWidget(simple_console_widget.SimpleConsoleWidget(self))
        self.addWidget(reconfigure_widget.ReconfigureWidget(self))
        self.addWidget(pyro_display_widget.PyroWidget(self))
        self.addWidget(complete_console_widget.CompleteConsoleWidget(self))
        self.addWidget(LocalSimWidget(self))

        self.widgetList[1].move(400, 0)  # Move the widgets to better spots
        self.widgetList[2].move(1000, 0)  # This isn't really the best way to reference the object, but I don't care
        self.widgetList[3].move(1000, 700)
        self.widgetList[4].move(1400, 700)
        self.widgetList[5].move(800, 700)
        self.widgetList[6].move(400, 700)

        self.canAddWidgets = True
