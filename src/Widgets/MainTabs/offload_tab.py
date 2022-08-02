"""
Blank tab with diagnostic boxes
"""

from src.Widgets import (
    board_usb_offloader_widget,
    complete_console_widget,
    simple_console_widget,
)
from src.Widgets.MainTabs.main_tab_common import TabCommon
from src.Widgets.offload_graph_widget import OffloadGraphWidget


class OffloadTab(TabCommon):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        simpleConsoleWidget = self.addWidget(simple_console_widget.SimpleConsoleWidget(self))
        completeConsoleWidget = self.addWidget(complete_console_widget.CLIUSBInterface(self))
        offloadWidget = self.addWidget(board_usb_offloader_widget.BoardCliWrapper(self))
        self.addWidget(OffloadGraphWidget(self))

        simpleConsoleWidget.move(1000, 0)
        offloadWidget.move(500, 0)
        completeConsoleWidget.move(0, 0)

        self.canAddWidgets = True
