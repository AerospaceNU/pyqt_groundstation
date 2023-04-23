"""
Blank tab with diagnostic boxes
"""
from src.Widgets import (
    pyro_display_widget,
    qr_code_widget,
    reconfigure_widget,
    simple_console_widget,
    diagnostics_widget,
)
from src.Widgets.complete_console_widget import CompleteConsoleWidget
from src.Widgets.MainTabs.main_tab_common import TabCommon


class DiagnosticTab(TabCommon):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.addWidget(diagnostics_widget.DiagnosticsWidget(self))
        self.addWidget(diagnostics_widget.DiagnosticsWidget(self))
        self.addWidget(simple_console_widget.SimpleConsoleWidget(self))
        self.addWidget(reconfigure_widget.ReconfigureWidget(self))
        self.addWidget(pyro_display_widget.PyroWidget(self))
        self.addWidget(qr_code_widget.RocketLocationQrCode(self)).move(0, 400)
        self.addWidget(CompleteConsoleWidget(self)).move(0, 200)

        self.widgetList[1].move(400, 0)  # Move the widgets to better spots
        self.widgetList[2].move(1000, 0)  # This isn't really the best way to reference the object, but I don't care
        self.widgetList[3].move(1000, 700)
        self.widgetList[4].move(1400, 700)

        self.canAddWidgets = True
