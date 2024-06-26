"""
A bunch of graphs
"""

from src.Widgets.MainTabs.GraphLayouts.fcb_offload_graphs import FcbOffloadGraphs
from src.Widgets.MainTabs.GraphLayouts.fcb_telem_graphs import FcbTelemetryGraphs
from src.Widgets.MainTabs.GraphLayouts.prop_stand_graphs import PropStandGraphs
from src.Widgets.MainTabs.side_tab_holder import SideTabHolder


class GraphsTab(SideTabHolder):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.addSubTab("FCB Telemetry", FcbTelemetryGraphs())
        self.addSubTab("FCB Offloaded Data", FcbOffloadGraphs())
        self.addSubTab("Prop Stand Graphs", PropStandGraphs())

        self.tab_widget.button_scroll_area.setMinimumWidth(200)
