"""
Blank tab with diagnostic boxes
"""

from src.MainTabs.main_tab_common import TabCommon
from src.Widgets import (
    board_usb_offloader_widget,
    complete_console_widget,
    simple_console_widget,
    offload_graph_widget,
)


class OffloadTab(TabCommon):
    def __init__(self, tab_name, parent=None):
        super().__init__(tab_name, parent=parent)
        simpleConsoleWidget = self.addWidget(simple_console_widget.SimpleConsoleWidget(self))
        completeConsoleWidget = self.addWidget(complete_console_widget.CLIUSBInterface(self))
        offloadWidget = self.addWidget(board_usb_offloader_widget.BoardCliWrapper(self))
        graphWidget = self.addWidget(offload_graph_widget.OffloadGraphWidget(self))

        simpleConsoleWidget.move(1000, 0)
        offloadWidget.move(500, 0)
        completeConsoleWidget.move(0, 0)

        self.canAddWidgets = True