"""
Tab that has all the prop stuff

"""
from PyQt5.QtWidgets import QGridLayout, QSizePolicy

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
        prop_graphs = self.addWidget(PropStandGraphs())
        text_box_widget = self.addWidget(TextBoxDropDownWidget(auto_size=False))
        console = self.addWidget(SimpleConsoleWidget())

        prop_graphs.layout().setContentsMargins(0, 0, 0, 0)
        text_box_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        text_box_widget.setMaximumHeight(300)
        text_box_widget.setMaximumWidth(400)
        console.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout.addWidget(prop_control_widget, 0, 0, 1, 2)
        layout.addWidget(self.addWidget(AnnunciatorPanel()), 1, 0, 1, 1)
        layout.addWidget(text_box_widget, 1, 1, 1, 1)
        layout.addWidget(console, 2, 0, 1, 2)
        layout.addWidget(prop_graphs, 0, 3, 3, 1)
