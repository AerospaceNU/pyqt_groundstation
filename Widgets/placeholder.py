"""
Frame rate counter

Actually doesn't count framerate right now

Just used to keep the gui updating if nothing else is drawing
"""

import time

from PyQt5.QtWidgets import QLabel


class Placeholder(QLabel):
    def __init__(self, widget):
        super().__init__(widget)
        self.move(-100, -100)

    def update(self):
        outString = str(time.time())
        self.setText(outString)
        self.adjustSize()
