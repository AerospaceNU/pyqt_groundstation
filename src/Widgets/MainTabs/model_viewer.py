"""
Blank tab with diagnostic boxes
"""
from PyQt5.QtWidgets import QGridLayout

from src.Widgets.MainTabs.main_tab_common import TabCommon
from src.Widgets import gl_display_widget


class ModelViewer(TabCommon):
    def __init__(self,  parent=None):
        super().__init__( parent=parent)

        self.viewer = self.addWidget(gl_display_widget.ThreeDDisplay())

        layout = QGridLayout()
        layout.addWidget(self.viewer)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
