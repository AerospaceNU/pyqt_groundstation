"""
Top bar of primary display to show vehicle status
"""

from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout

from Widgets import custom_q_widget_base
from Widgets.QWidget_Parts import simple_bar_graph_widget
from constants import Constants
from data_helpers import get_value_from_dictionary, round_to_string


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
        self.line_cutter_batt_1_graph = simple_bar_graph_widget.SimpleBarGraphWidget(title="LC1 Batt", minValue=7.4, maxValue=8.2)
        self.line_cutter_batt_2_graph = simple_bar_graph_widget.SimpleBarGraphWidget(title="LC2 Batt", minValue=7.4, maxValue=8.2)
        self.fcb_memory_graph = simple_bar_graph_widget.SimpleBarGraphWidget(title="FCB Mem", minValue=0, maxValue=1, barColor="rgb(255,0,0)")

        layout = QGridLayout()
        layout.addWidget(self.statusBox, 1, 1, 4, 1)
        layout.addWidget(self.fcb_state_box, 1, 2, 4, 1)
        layout.addWidget(self.modeBox, 1, 3, 4, 1)
        layout.addWidget(self.rssi_box, 1, 4)
        layout.addWidget(self.message_age_box, 2, 4)
        layout.addWidget(self.v_speed_box, 3, 4)
        layout.addWidget(self.acceleration_box, 4, 4)
        layout.addWidget(self.fcb_battery_graph, 1, 6, 4, 1)
        layout.addWidget(self.prop_battery_graph, 1, 7, 4, 1)
        layout.addWidget(self.line_cutter_batt_1_graph, 1, 8, 4, 1)
        layout.addWidget(self.line_cutter_batt_2_graph, 1, 9, 4, 1)
        layout.addWidget(self.fcb_memory_graph, 1, 10, 4, 1)
        layout.setContentsMargins(1, 1, 3, 1)
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
        self.addSourceKey("lc1_voltage", float, Constants.line_cutter_1_voltage, -1, hide_in_drop_down=True)
        self.addSourceKey("lc2_voltage", float, Constants.line_cutter_2_voltage, -1, hide_in_drop_down=True)
        self.addSourceKey("fcb_mem", float, Constants.fcb_memory_usage, -1, hide_in_drop_down=True)

        self.statusBox.setFont(QFont("Monospace", self.widgetSize))
        self.statusBox.setAlignment(QtCore.Qt.AlignCenter)
        self.statusBox.setMinimumWidth(self.widgetSize * 8)

        self.fcb_state_box.setFont(QFont("Monospace", self.widgetSize))
        self.fcb_state_box.setAlignment(QtCore.Qt.AlignCenter)
        self.fcb_state_box.setMinimumWidth(self.widgetSize * 13)

        self.modeBox.setFont(QFont("Monospace", self.widgetSize))
        self.modeBox.setAlignment(QtCore.Qt.AlignCenter)
        self.modeBox.setMinimumWidth(self.widgetSize * 13)

        for box in [self.rssi_box, self.message_age_box, self.v_speed_box, self.acceleration_box]:
            box.setFont(QFont("Monospace", self.widgetSize * 0.4))

        self.statusBox.adjustSize()
        self.fcb_state_box.adjustSize()
        self.modeBox.adjustSize()
        self.setMaximumHeight(self.modeBox.height() * 2 + 20)

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
            self.statusBox.setStyleSheet("color: red")
            self.statusBox.setText("Faulted")
        elif fault_status == 1:
            self.statusBox.setStyleSheet("color: yellow")
            self.statusBox.setText("Warning")
        elif fault_status == 0:
            self.statusBox.setStyleSheet("color: green")
            self.statusBox.setText("OK")
        else:
            self.statusBox.setStyleSheet("color: blue")
            self.statusBox.setText("Unknown")

        self.fcb_state_box.setText(fcb_state)

        self.modeBox.setText("Alt: {} m".format(round_to_string(altitude, 6)))
        self.rssi_box.setText("RSSI: {}".format(rssi))
        self.message_age_box.setText("Message age: {} s".format(message_age))
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

    def setWidgetColors(self, widget_background_string, text_string, header_text_string, border_string):
        self.modeBox.setStyleSheet(text_string)
        self.rssi_box.setStyleSheet(text_string)
        self.message_age_box.setStyleSheet(text_string)
        self.v_speed_box.setStyleSheet(text_string)
        self.acceleration_box.setStyleSheet(text_string)
        self.fcb_state_box.setStyleSheet(text_string)

        self.fcb_battery_graph.setTextColor(text_string)
        self.prop_battery_graph.setTextColor(text_string)
        self.line_cutter_batt_1_graph.setTextColor(text_string)
        self.line_cutter_batt_2_graph.setTextColor(text_string)
        self.fcb_memory_graph.setTextColor(text_string)
