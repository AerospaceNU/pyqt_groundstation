import pyqtgraph

PEN_COLORS = ["red", "blue", "green", "magenta"]

LINE_WIDTH = 2


def get_pen_from_line_number(line_number):
    index = line_number % len(PEN_COLORS)
    return pyqtgraph.mkPen(color=PEN_COLORS[index], width=LINE_WIDTH)
