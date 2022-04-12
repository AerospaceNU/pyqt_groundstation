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


class LineCutterControl(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None):
        super().__init__(parent_widget)

        self.line_cutter_options = []
        self.active_line_cutter = 0

        self.armed = False

        self.select_box = QComboBox()
        self.refresh_button = QPushButton()
        self.state_text_box = QLabel()
        self.state_data_box = QLabel()
        self.light_text_box = QLabel()
        self.light_data_graph = sideways_bar_graph.SidewaysBarGraph(min_value=0, max_value=1023, mid_value=-1)
        self.cut_1_label = QLabel()
        self.cut_2_label = QLabel()
        self.cut_1_box = QLabel()
        self.cut_2_box = QLabel()
        self.armed_button = QPushButton()
        self.cut_1_button = QPushButton()
        self.cut_2_button = QPushButton()

        layout = QGridLayout()

        header_layout = QGridLayout()
        header_layout.addWidget(self.select_box, 1, 1)
        header_layout.addWidget(self.refresh_button, 1, 2)
        layout.addLayout(header_layout, 1, 1)

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
        indicator_box_layout.addWidget(self.armed_button, 3, 1, 1, 2)
        indicator_box_layout.addWidget(self.cut_1_button, 4, 1)
        indicator_box_layout.addWidget(self.cut_2_button, 4, 2)
        layout.addLayout(indicator_box_layout, 3, 1)

        self.setLayout(layout)

        self.refresh_button.setText("Refresh")
        self.state_text_box.setText("State:")
        self.light_text_box.setText("Light:")
        self.cut_1_label.setText("Cut 1")
        self.cut_2_label.setText("Cut 2")
        self.armed_button.setText("Arm")
        self.cut_1_button.setText("Cut Line 1")
        self.cut_2_button.setText("Cut Line 2")

        self.cut_1_label.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.cut_1_box.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.cut_2_label.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.cut_2_box.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

        self.select_box.setMinimumWidth(150)
        self.state_text_box.setMaximumWidth(50)
        self.light_text_box.setMaximumWidth(50)

        self.state_text_box.adjustSize()
        self.light_text_box.adjustSize()

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
        current_line_cutter_num = int(current_line_cutter[-1])

        state_key = Constants.makeLineCutterString(current_line_cutter_num, Constants.line_cutter_state_key)
        light_key = Constants.makeLineCutterString(current_line_cutter_num, Constants.photoresistor_key)
        light_threshold_key = Constants.makeLineCutterString(current_line_cutter_num, Constants.photoresistor_threshold_key)
        cut_1_key = Constants.makeLineCutterString(current_line_cutter_num, Constants.line_cutter_cut_1)
        cut_2_key = Constants.makeLineCutterString(current_line_cutter_num, Constants.line_cutter_cut_2)

        state = str(get_value_from_dictionary(vehicle_data, state_key, "No Data"))
        light = int(get_value_from_dictionary(vehicle_data, light_key, -1))
        light_threshold = int(get_value_from_dictionary(vehicle_data, light_threshold_key, -1))
        cut_1 = str(get_value_from_dictionary(vehicle_data, cut_1_key, "false")).lower() == "true"
        cut_2 = str(get_value_from_dictionary(vehicle_data, cut_2_key, "false")).lower() == "true"

        self.state_data_box.setText(state)
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

    def setWidgetColors(self, widget_background_string, text_string, header_text_string, border_string):
        self.select_box.setStyleSheet(widget_background_string + text_string)
        self.refresh_button.setStyleSheet(widget_background_string + text_string)
        self.state_text_box.setStyleSheet(widget_background_string + text_string)
        self.state_data_box.setStyleSheet(widget_background_string + text_string)
        self.light_text_box.setStyleSheet(widget_background_string + text_string)
        self.light_data_graph.setStyleSheet(widget_background_string + text_string)

        self.cut_1_label.setStyleSheet(widget_background_string + text_string)
        self.cut_2_label.setStyleSheet(widget_background_string + text_string)
        self.armed_button.setStyleSheet(widget_background_string + text_string)
        self.cut_1_button.setStyleSheet(widget_background_string + text_string)
        self.cut_2_button.setStyleSheet(widget_background_string + text_string)
