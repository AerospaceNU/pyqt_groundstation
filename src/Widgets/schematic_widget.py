import json

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPen
from PyQt5.QtWidgets import QWidget

from src.Widgets.custom_q_widget_base import CustomQWidgetBase

BASE_WIDTH = 1900
BASE_HEIGHT = 1000
VALVE_DIAMETER = 50


class SchematicWidget(CustomQWidgetBase):
    def __init__(self, source, parent_widget: QWidget = None):
        super().__init__(parent_widget)
        self.color_dict = {"green": Qt.GlobalColor.darkGreen, "blue": Qt.GlobalColor.darkCyan, "yellow": QColor(197, 90, 0, 255), "purple": Qt.GlobalColor.darkMagenta}
        self.valve_colors = {"open": Qt.GlobalColor.green, "closed": Qt.GlobalColor.red, "unknown": Qt.GlobalColor.gray}
        self.painter = QPainter()
        self.vehicle_data = {}

        self.schematic_layout = json.load(open(source))
        self.show()

    def paintEvent(self, event):
        if len(self.vehicle_data) == 0:
            # Return if vehicleData is just empty
            return
        self.painter.begin(self)
        schematic = self.schematic_layout
        old_pen = QPen(self.painter.pen())
        for group_name, point_list in schematic["edges"].items():
            self.painter.setPen(QPen(self.color_dict[schematic["nodeGroups"][group_name]], 8, Qt.PenStyle.SolidLine))
            for line_pair in point_list:
                mapped_pair = list(map(lambda point: self._scaled_remap(point), line_pair))
                self.painter.drawLine(*(mapped_pair[0] + mapped_pair[1]))

        self.painter.setPen(old_pen)
        for valve in schematic["nodes"]["valves"]:
            self._draw_valve(valve)

        for rect in schematic["nodes"]["rectangles"]:
            self._draw_rectangle(rect)

        self.painter.setPen(old_pen)
        font = QFont()
        font.setPointSize(12)
        self.painter.setFont(font)

        for label in schematic["data_labels"]:
            if label["name"] in self.vehicle_data:
                self.painter.drawText(*(self._scaled_remap(label["pos"])), 200, 25, Qt.AlignmentFlag.AlignBaseline, f"{label['name']}: {self.vehicle_data[label['name']]:.1f} {label['unit']}")

        self.painter.setPen(old_pen)
        self.painter.end()

    def _draw_valve(self, valve):
        valve_state = None
        self.painter.setBrush(self.valve_colors["unknown"])
        if valve["name"] in self.vehicleData:
            valve_state = self.vehicleData[valve["name"]].lower()
            if valve_state in self.valve_colors:
                self.painter.setBrush(self.valve_colors[valve_state])

        pos = self._scaled_remap(valve["pos"])

        self.painter.drawEllipse(pos[0] - VALVE_DIAMETER / 2, pos[1] - VALVE_DIAMETER / 2, VALVE_DIAMETER, VALVE_DIAMETER)
        old_pen = QPen(self.painter.pen())
        self.painter.setPen(QPen(Qt.GlobalColor.black, 6, Qt.PenStyle.SolidLine))
        if valve_state:
            # Using some boolean logic, if the "horizontalness" and "openness" of the valves are the same, the line should be horizontal
            # Otherwise, the line should be vertical
            # From the following truth table
            #       Horizontal
            #         T  F
            # Open T  H  V
            #      F  V  H
            if (valve["flow"] == "horizontal") == (valve_state == "open"):
                self.painter.drawLine(pos[0] - VALVE_DIAMETER / 2 + 3, pos[1], pos[0] + VALVE_DIAMETER / 2 - 3, pos[1])
            else:
                self.painter.drawLine(pos[0], pos[1] - VALVE_DIAMETER / 2 + 3, pos[0], pos[1] + VALVE_DIAMETER / 2 - 3)
        self.painter.setPen(old_pen)
        font = QFont()
        font.setPointSize(12)
        self.painter.setFont(font)
        label_pos = []
        if valve["label"] == "right":
            label_pos = [pos[0] + 40, pos[1]]
        elif valve["label"] == "left":
            label_pos = [pos[0] - 100, pos[1]]
        elif valve["label"] == "below":
            label_pos = [pos[0] - 25, pos[1] + 50]
        else:
            label_pos = [pos[0] - 25, pos[1] - 30]
        self.painter.drawText(label_pos[0], label_pos[1], valve["name"])

    def _draw_rectangle(self, rect):
        font = QFont()
        font.setPointSize(15)
        schematic = self.schematic_layout
        self.painter.setBrush(self.color_dict[schematic["nodeGroups"][rect["group"]]])
        scaled_pos = self._scaled_remap(rect["pos"])
        scaled_dim = self._scaled_remap(rect["dim"])
        center = [scaled_pos[i] - (scaled_dim[i] / 2) for i, _ in enumerate(scaled_pos)]
        self.painter.drawRect(*(center + scaled_dim))
        self.painter.setFont(font)
        self.painter.drawText(center[0], center[1], scaled_dim[0], scaled_dim[1], Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, rect["name"])

    def _scaled_remap(self, point):
        # Maps a point from the dimension of the schematic to our actual widget
        return [(point[0] / BASE_WIDTH) * self.width(), (point[1] / BASE_HEIGHT) * self.height()]

    def updateData(self, vehicle_data, updated_data):
        self.vehicle_data = vehicle_data
