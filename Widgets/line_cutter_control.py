"""
Text box widget
"""
from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QWidget, QGridLayout, QComboBox, QPushButton
from PyQt5.QtGui import QFont

from Widgets import custom_q_widget_base
from Widgets.QWidget_Parts import sideways_bar_graph

from constants import Constants
from data_helpers import get_value_from_dictionary

LINE_CUTTER_COMMON_TEXT = "line_cutter_"
STATES = ["WAITING", "ARMED", "DEPLOYED", "PARTIAL_DISREEF", "FULL_DISREEF", "LANDED"]


class LineCutterControl(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None):
        super().__init__(parent_widget)

        self.line_cutter_options = []
        self.active_line_cutter = 0

        self.cutter_enabled = False
        self.cutter_armed = False

        self.select_box = QComboBox()
        self.state_text_box = QLabel()
        self.state_data_box = QLabel()
        self.light_text_box = QLabel()
        self.light_data_graph = sideways_bar_graph.SidewaysBarGraph(min_value=0, max_value=1023, mid_value=-1)
        self.cut_1_label = QLabel()
        self.cut_2_label = QLabel()
        self.cut_1_box = QLabel()
        self.cut_2_box = QLabel()
        self.cutting_enable_button = QPushButton()
        self.cut_1_button = QPushButton()
        self.cut_2_button = QPushButton()
        self.arm_button = QPushButton()

        layout = QGridLayout()
        layout.addWidget(self.select_box, 1, 1)

        data_view_layout = QGridLayout()
        data_view_layout.addWidget(self.state_text_box, 1, 1)
        data_view_layout.addWidget(self.state_data_box, 1, 2)
        data_view_layout.addWidget(self.light_text_box, 2, 1)
        data_view_layout.addWidget(self.light_data_graph, 2, 2)
        layout.addLayout(data_view_layout, 2, 1)

        indicator_box_layout = QGridLayout()
        indicator_box_layout.addWidget(self.cut_1_label, 1, 1)
        indicator_box_layout.addWidget(self.cut_2_label, 1, 2)
        indicator_box_layout.addWidget(self.cut_1_box, 2, 1)
        indicator_box_layout.addWidget(self.cut_2_box, 2, 2)
        indicator_box_layout.addWidget(self.cutting_enable_button, 3, 1, 1, 2)
        indicator_box_layout.addWidget(self.cut_1_button, 4, 1)
        indicator_box_layout.addWidget(self.cut_2_button, 4, 2)
        indicator_box_layout.addWidget(self.arm_button, 5, 1, 1, 2)
        layout.addLayout(indicator_box_layout, 3, 1)

        self.setLayout(layout)

        self.state_text_box.setText("State:")
        self.light_text_box.setText("Light:")
        self.cut_1_label.setText("Cut 1")
        self.cut_2_label.setText("Cut 2")
        self.cutting_enable_button.setText("Enable Commands")
        self.cut_1_button.setText("Cut Line 1")
        self.cut_2_button.setText("Cut Line 2")
        self.arm_button.setText("Arm Line Cutter")

        self.cut_1_label.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.cut_1_box.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.cut_2_label.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.cut_2_box.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

        self.setMinimumWidth(250)
        self.state_text_box.setMaximumWidth(50)
        self.light_text_box.setMaximumWidth(50)

        self.state_text_box.adjustSize()
        self.light_text_box.adjustSize()

        self.cutting_enable_button.clicked.connect(self.onEnableButtonPress)
        self.cut_1_button.clicked.connect(lambda: self.onCutButtonPressed(1))
        self.cut_2_button.clicked.connect(lambda: self.onCutButtonPressed(2))
        self.arm_button.clicked.connect(self.onArmButtonPressed)

    def onEnableButtonPress(self):
        self.setCutterEnabledOrDisabled(not self.cutter_enabled)

    def onCutButtonPressed(self, button_number):
        if self.cutter_enabled:
            self.callbackEvents.append([Constants.cli_interface_key, "--line_cutter -i {0} -c '!fire {1}'".format(self.active_line_cutter, button_number)])  # Replace this with whatever fire command you want
        self.setCutterEnabledOrDisabled(False)

    def onArmButtonPressed(self):
        self.setArmOrDisarm(not self.cutter_armed)

    def setCutterEnabledOrDisabled(self, enabled):
        self.cutter_enabled = enabled
        if self.cutter_enabled:
            self.cutting_enable_button.setText("Disable Commands")
        else:
            self.cutting_enable_button.setText("Enable Commands")

    def setArmOrDisarm(self, armed):
        self.cutter_armed = armed
        if self.cutter_armed:
            self.arm_button.setText("Disarm Line Cutter")
            self.callbackEvents.append([Constants.cli_interface_key, "--line_cutter -i {0} -c '!arm'".format(self.active_line_cutter)])
        else:
            self.arm_button.setText("Arm Line Cutter")
            self.callbackEvents.append([Constants.cli_interface_key, "--line_cutter -i {0} -c '!disarm'".format(self.active_line_cutter)])

    def updateData(self, vehicle_data, updated_data):
        line_cutter_options = []

        for key in vehicle_data:  # Figure out how many line cutters we have connected
            if LINE_CUTTER_COMMON_TEXT in key:
                next_char = key[len(LINE_CUTTER_COMMON_TEXT)]

                try:
                    data = int(next_char)
                    if data not in line_cutter_options:
                        line_cutter_options.append(data)
                except:
                    pass

        line_cutter_options.sort()

        if line_cutter_options != self.line_cutter_options:  # Set new drop down menu
            self.line_cutter_options = line_cutter_options

            text_options = []
            for option in self.line_cutter_options:
                text_options.append("Line Cutter {0}".format(option))
                self.select_box.clear()
                self.select_box.addItems(text_options)

            self.select_box.adjustSize()

        current_line_cutter = self.select_box.currentText()
        if current_line_cutter == "":
            return
        self.active_line_cutter = int(current_line_cutter[-1])

        state_key = Constants.makeLineCutterString(self.active_line_cutter, Constants.line_cutter_state_key)
        light_key = Constants.makeLineCutterString(self.active_line_cutter, Constants.photoresistor_key)
        light_threshold_key = Constants.makeLineCutterString(self.active_line_cutter, Constants.photoresistor_threshold_key)
        cut_1_key = Constants.makeLineCutterString(self.active_line_cutter, Constants.line_cutter_cut_1)
        cut_2_key = Constants.makeLineCutterString(self.active_line_cutter, Constants.line_cutter_cut_2)

        state_num = int(get_value_from_dictionary(vehicle_data, state_key, -1))
        light = int(get_value_from_dictionary(vehicle_data, light_key, -1))
        light_threshold = int(get_value_from_dictionary(vehicle_data, light_threshold_key, -1))
        cut_1 = str(get_value_from_dictionary(vehicle_data, cut_1_key, "false")).lower() == "true"
        cut_2 = str(get_value_from_dictionary(vehicle_data, cut_2_key, "false")).lower() == "true"

        if 0 <= state_num < len(STATES):
            state_text = STATES[state_num]
        else:
            state_text = "Unknown State"

        self.state_data_box.setText(state_text)
        self.light_data_graph.setValue(light)
        self.light_data_graph.setMidValue(light_threshold)

        if cut_1:
            self.cut_1_box.setStyleSheet("background: green; color: black")
            self.cut_1_box.setText("Good")
        else:
            self.cut_1_box.setStyleSheet("background: red; color: black")
            self.cut_1_box.setText("Error")

        if cut_2:
            self.cut_2_box.setStyleSheet("background: green; color: black")
            self.cut_2_box.setText("Good")
        else:
            self.cut_2_box.setStyleSheet("background: red; color: black")
            self.cut_2_box.setText("Error")

        self.update()

    def setWidgetColors(self, widget_background_string, text_string, header_text_string, border_string):
        self.select_box.setStyleSheet(widget_background_string + text_string)
        self.state_text_box.setStyleSheet(widget_background_string + text_string)
        self.state_data_box.setStyleSheet(widget_background_string + text_string)
        self.light_text_box.setStyleSheet(widget_background_string + text_string)
        self.light_data_graph.setStyleSheet(widget_background_string + text_string)

        self.cut_1_label.setStyleSheet(widget_background_string + text_string)
        self.cut_2_label.setStyleSheet(widget_background_string + text_string)
        self.cutting_enable_button.setStyleSheet(widget_background_string + text_string)
        self.cut_1_button.setStyleSheet(widget_background_string + text_string)
        self.cut_2_button.setStyleSheet(widget_background_string + text_string)
        self.arm_button.setStyleSheet(widget_background_string + text_string)
