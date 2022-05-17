"""
Blank tab with diagnostic boxes
"""

from Widgets import simple_console_widget
from Widgets import complete_console_widget

from MainTabs.main_tab_common import TabCommon


class OffloadTab(TabCommon):
    def __init__(self, tab_name, parent=None):
        super().__init__(tab_name, parent=parent)
        simpleConsoleWidget = self.addWidget(simple_console_widget.SimpleConsoleWidget(self))
        completeConsoleWidget = self.addWidget(complete_console_widget.CompleteConsoleWidget(self))

        simpleConsoleWidget.move(1000, 0)
        completeConsoleWidget.move(0, 0)

        self.canAddWidgets = True
