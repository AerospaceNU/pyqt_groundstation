from PyQt5.QtWidgets import QGridLayout

from src.Widgets.graph_widget import GraphWidget
from src.Widgets.MainTabs.GraphLayouts.graph_layout import GraphLayoutCommon


class PropStandGraphs(GraphLayoutCommon):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        layout = QGridLayout()
        layout.addWidget(self.addWidget(GraphWidget(title="Kerosene Pressure", source_list=["kerInletDucer", "kerPintleDucer", "kerTankDucer", "kerVenturi"])), 1, 1)
        layout.addWidget(self.addWidget(GraphWidget(title="LOX Pressure", source_list=["loxInletDucer", "loxPintleDucer", "loxTankDucer", "loxVenturi"])), 1, 2)
        layout.addWidget(self.addWidget(GraphWidget(title="Other Pressure", source_list=["pneumaticDucer", "purgeDucer"])), 1, 3)
        layout.addWidget(self.addWidget(GraphWidget(title="Load Cell", source_list=["loadCell"])), 2, 1)
        layout.addWidget(self.addWidget(GraphWidget(title="Manifold Thermocouples", source_list=["manifoldInletThermo", "manifoldOutletThermo"])), 2, 2)
        layout.addWidget(self.addWidget(GraphWidget(title="Tank Thermocouples", source_list=["tank1Thermo", "tank2Thermo", "tank3Thermo"])), 2, 3)
        # layout.addWidget(self.addWidget(GraphWidget(title="Ker", source_list=[Constants.barometer_pressure_key, Constants.barometer_pressure_2_key, Constants.press_ref_key, ], )), 3, 1)
        # layout.addWidget(self.addWidget(GraphWidget(title="State", source_list=[Constants.fcb_state_number_key])), 3, 2)
        # layout.addWidget(self.addWidget(GraphWidget(title="RSSI", source_list=[Constants.rssi_val_key])), 3, 3)
        layout.addWidget(self.graphControlWidget, 4, 1, 1, 3)
        self.setLayout(layout)
