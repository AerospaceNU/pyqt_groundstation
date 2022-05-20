"""
Blank tab with diagnostic boxes
"""
from PyQt5.QtWidgets import QGridLayout

from Widgets import gl_display_widget

from MainTabs.main_tab_common import TabCommon


class ModelViewer(TabCommon):
    def __init__(self, tab_name, parent=None):
        super().__init__(tab_name, parent=parent)

        self.viewer = self.addWidget(gl_display_widget.ThreeDDisplay(self))

        layout = QGridLayout()
        layout.addWidget(self.viewer)
        self.setLayout(layout)
