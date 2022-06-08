"""
A bunch of graphs
"""

from PyQt5.QtWidgets import QVBoxLayout
from src.Widgets.MainTabs.GraphLayouts.fcb_offload_graphs import FcbOffloadGraphs
from src.Widgets.MainTabs.GraphLayouts.fcb_telem_graphs import FcbTelemetryGraphs
from src.Widgets.MainTabs.side_tab_holder import SideTabHolder

from src.constants import Constants
from src.data_helpers import interpolate
from src.Widgets.MainTabs.main_tab_common import TabCommon
from src.Widgets.graph_tab_control import GraphTabControl
from src.Widgets.graph_widget import GraphWidget


class GraphsTab(TabCommon):
    def __init__(self,  parent=None):
        super().__init__( parent=parent)

        self.slider_min = 0
        self.slider_max = 1000

        layout = QVBoxLayout()
        self.tabs = SideTabHolder()
        self.tabs.addSubTab("FCB Telemetry", FcbTelemetryGraphs())
        self.tabs.addSubTab("FCB Offloaded Data", FcbOffloadGraphs())
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def customUpdateVehicleData(self, data):
        self.tabs.customUpdateVehicleData(data)