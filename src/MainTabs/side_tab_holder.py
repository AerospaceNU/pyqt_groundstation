"""
Custom tab to hold other tabs with the tab bar on the side
"""

from PyQt5.QtWidgets import QGridLayout

from src.MainTabs.main_tab_common import TabCommon
from src.MainTabs.sub_tab_holder_common import SubTabHolder
from src.Widgets.QWidget_Parts.side_tab_widget import SideTabWidget


class SideTabHolder(SubTabHolder):
    def __init__(self, tab_name, parent=None):
        super().__init__(tab_name, parent=parent)

        self.tab_widget = SideTabWidget()

        layout = QGridLayout()
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def addSubTab(self, tab_name: str, tab_object: TabCommon):
        self.tab_widget.addTab(tab_name, tab_object)
        super(SideTabHolder, self).addSubTab(tab_name, tab_object)
