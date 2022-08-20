from PyQt5.QtWidgets import QGridLayout, QSizePolicy

from src.Widgets.MainTabs.main_tab_common import TabCommon
from src.Widgets.schematic_widget import SchematicWidget


class PropSchematicTab(TabCommon):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = QGridLayout()
        self.setLayout(layout)
        schematic = SchematicWidget("src/Assets/prop_schematic_parts.json", self)
        schematic.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        schematic.setMinimumWidth(400)
        schematic.setMinimumHeight(400)
        layout.addWidget(schematic)
        self.addWidget(schematic)
