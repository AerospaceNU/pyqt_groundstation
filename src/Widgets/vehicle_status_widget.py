"""
Top bar of primary display to show vehicle status
"""

from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget

from src.constants import Constants
from src.data_helpers import round_to_string
from src.Widgets import custom_q_widget_base
from src.Widgets.QWidget_Parts import simple_bar_graph_widget


class VehicleStatusWidget(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, widget: QWidget = None):
        super().__init__(widget)
        self.statusBox = QLabel()
        self.fcb_state_box = QLabel()
        self.modeBox = QLabel()
        self.rssi_box = QLabel()
        self.message_age_box = QLabel()
        self.v_speed_box = QLabel()
        self.acceleration_box = QLabel()

        self.fcb_battery_graph = simple_bar_graph_widget.SimpleBarGraphWidget(title="FCB Batt", minValue=11.1, maxValue=12.6)
        self.prop_battery_graph = simple_bar_graph_widget.SimpleBarGraphWidget(title="Prop Batt", minValue=0, maxValue=10)
        self.line_cutter_batt_1_graph = simple_bar_graph_widget.SimpleBarGraphWidget(title="LC1 Batt", minValue=3.7, maxValue=4.2)
        self.line_cutter_batt_2_graph = simple_bar_graph_widget.SimpleBarGraphWidget(title="LC2 Batt", minValue=3.7, maxValue=4.2)
        self.fcb_memory_graph = simple_bar_graph_widget.SimpleBarGraphWidget(title="FCB Mem", minValue=0, maxValue=1, barColor="rgb(255,0,0)")

        layout = QHBoxLayout()
        layout.addWidget(self.statusBox)
        layout.addWidget(self.fcb_state_box)
        layout.addWidget(self.modeBox)

        vbox = QVBoxLayout()
        vbox.addWidget(self.rssi_box)
        vbox.addWidget(self.message_age_box)
        vbox.addWidget(self.v_speed_box)
        vbox.addWidget(self.acceleration_box)
        vbox.setContentsMargins(1, 1, 1, 0)
        layout.addLayout(vbox)

        layout.addWidget(self.fcb_battery_graph)
        layout.addWidget(self.prop_battery_graph)
        layout.addWidget(self.line_cutter_batt_1_graph)
        layout.addWidget(self.line_cutter_batt_2_graph)
        layout.addWidget(self.fcb_memory_graph, )

        layout.setContentsMargins(1, 1, 1, 1)
        self.setLayout(layout)

        self.widgetSize = 20
        self.title = None
        self.font = None
        self.fontSize = None

        self.addSourceKey("status_source", int, Constants.status_source, 3, hide_in_drop_down=True)
        self.addSourceKey("fcb_state", str, Constants.fcb_state_key, "No Data", hide_in_drop_down=True)
        self.addSourceKey("altitude", float, Constants.altitude_key, -1, hide_in_drop_down=True)
        self.addSourceKey("rssi", str, Constants.rssi_key, "No Data", hide_in_drop_down=True)
        self.addSourceKey("message_age", float, Constants.message_age_key, -1, hide_in_drop_down=True)
        self.addSourceKey("v_speed", float, Constants.vertical_speed_key, -1, hide_in_drop_down=True)
        self.addSourceKey("acceleration", float, Constants.acceleration_key, -1, hide_in_drop_down=True)
        self.addSourceKey("fcb_voltage", float, Constants.fcb_battery_voltage, -1, hide_in_drop_down=True)
        self.addSourceKey("prop_voltage", float, Constants.prop_battery_voltage, -1, hide_in_drop_down=True)
        self.addSourceKey("lc1_voltage", float, Constants.makeLineCutterString(0, Constants.battery_voltage_key), -1, hide_in_drop_down=False)
        self.addSourceKey("lc2_voltage", float, Constants.makeLineCutterString(1, Constants.battery_voltage_key), -1, hide_in_drop_down=False)
        self.addSourceKey("fcb_mem", float, Constants.fcb_memory_usage, -1, hide_in_drop_down=True)

        self.customUpdateAfterThemeSet()

    def customUpdateAfterThemeSet(self):
        self.statusBox.setAlignment(QtCore.Qt.AlignCenter)
        self.statusBox.setMinimumWidth(self.widgetSize * 8)

        self.fcb_state_box.setStyleSheet("font: {}pt Monospace".format(self.widgetSize))
        self.fcb_state_box.setAlignment(QtCore.Qt.AlignCenter)
        self.fcb_state_box.setMinimumWidth(self.widgetSize * 13)

        self.modeBox.setStyleSheet("font: {}pt Monospace".format(self.widgetSize))
        self.modeBox.setAlignment(QtCore.Qt.AlignCenter)
        self.modeBox.setMinimumWidth(self.widgetSize * 13)

        for box in [self.rssi_box, self.message_age_box, self.v_speed_box, self.acceleration_box]:
            box.setStyleSheet("font: {}pt Monospace".format(self.widgetSize * 0.4))
            box.setMaximumHeight(box.fontInfo().pixelSize() + 3)

        self.setMaximumHeight(self.widgetSize * 5)

        self.statusBox.adjustSize()
        self.fcb_state_box.adjustSize()
        self.modeBox.adjustSize()

        for widget in [self.fcb_battery_graph, self.prop_battery_graph, self.line_cutter_batt_1_graph, self.line_cutter_batt_2_graph, self.fcb_memory_graph]:
            widget.setTextColor(self.palette().text().color())
            widget.adjustSize()

    def updateInFocus(self):
        fault_status = self.getDictValueUsingSourceKey("status_source")
        fcb_state = self.getDictValueUsingSourceKey("fcb_state")
        altitude = self.getDictValueUsingSourceKey("altitude")
        rssi = self.getDictValueUsingSourceKey("rssi")
        message_age = self.getDictValueUsingSourceKey("message_age")
        v_speed = self.getDictValueUsingSourceKey("v_speed")
        acceleration = self.getDictValueUsingSourceKey("acceleration")
        fcb_voltage = self.getDictValueUsingSourceKey("fcb_voltage")
        prop_voltage = self.getDictValueUsingSourceKey("prop_voltage")
        lc1_voltage = self.getDictValueUsingSourceKey("lc1_voltage")
        lc2_voltage = self.getDictValueUsingSourceKey("lc2_voltage")
        fcb_mem = self.getDictValueUsingSourceKey("fcb_mem")

        if fault_status == 2:
            self.statusBox.setStyleSheet("color: red; font: {}pt Monospace".format(self.widgetSize))
            self.statusBox.setText("Faulted")
        elif fault_status == 1:
            self.statusBox.setStyleSheet("color: yellow; font: {}pt Monospace".format(self.widgetSize))
            self.statusBox.setText("Warning")
        elif fault_status == 0:
            self.statusBox.setStyleSheet("color: green; font: {}pt Monospace".format(self.widgetSize))
            self.statusBox.setText("OK")
        else:
            self.statusBox.setStyleSheet("color: blue; font: {}pt Monospace".format(self.widgetSize))
            self.statusBox.setText("Unknown")

        self.fcb_state_box.setText(fcb_state)

        self.modeBox.setText("Alt: {} m".format(round_to_string(altitude, 6)))
        self.rssi_box.setText("RSSI: {}".format(rssi))
        self.message_age_box.setText("Message age: {0:.2f} s".format(message_age))
        self.v_speed_box.setText("Vertical Speed: {} m/s".format(round_to_string(v_speed, 6)))
        self.acceleration_box.setText("Acceleration: {} m/s^2".format(round_to_string(acceleration, 6)))

        self.fcb_battery_graph.fixWidth(0.7)
        self.prop_battery_graph.fixWidth(0.7)
        self.line_cutter_batt_1_graph.fixWidth(0.7)
        self.line_cutter_batt_2_graph.fixWidth(0.7)
        self.fcb_memory_graph.fixWidth(0.7)

        self.fcb_battery_graph.setValue(fcb_voltage)
        self.prop_battery_graph.setValue(prop_voltage)
        self.line_cutter_batt_1_graph.setValue(lc1_voltage)
        self.line_cutter_batt_2_graph.setValue(lc2_voltage)
        self.fcb_memory_graph.setValue(fcb_mem)
