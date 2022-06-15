"""
Tab that has all the prop stuff

"""
from PyQt5.QtWidgets import QGridLayout

from src.Widgets.MainTabs.main_tab_common import TabCommon
from src.Widgets.simple_console_widget import SimpleConsoleWidget
from src.Widgets.text_box_drop_down_widget import TextBoxDropDownWidget
from src.Widgets.prop_control_widget import PropControlWidget
from src.Widgets.annunciator_panel import AnnunciatorPanel
from src.Widgets.MainTabs.GraphLayouts.prop_stand_graphs import PropStandGraphs


class PropViewTab(TabCommon):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = QGridLayout()
        self.setLayout(layout)

        prop_control_widget = self.addWidget(PropControlWidget())

        layout.addWidget(prop_control_widget, 0, 0, 1, 2)
        layout.addWidget(self.addWidget(AnnunciatorPanel()), 1, 0, 1, 1)
        layout.addWidget(self.addWidget(TextBoxDropDownWidget(auto_size=False)), 1, 1, 1, 1)
        layout.addWidget(self.addWidget(SimpleConsoleWidget()), 2, 0, 1, 2)

        graph_layout = QGridLayout()
        graph_layout.addWidget(self.addWidget(PropStandGraphs()), 1, 1)

        graph_layout.setContentsMargins(0, 0, 0, 0)

        layout.addLayout(graph_layout, 0, 3, 3, 1)
