"""
Prop Control Widget
"""

import json
import typing
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QComboBox, QGridLayout, QLabel, QWidget, QPushButton, QCheckBox, QFileSystemModel, QTreeView
import PyQt5.QtCore as QtCore

from src.constants import Constants
from src.Widgets import custom_q_widget_base

from src.data_helpers import get_value_from_dictionary

class LoggerConfigWidget(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.model = QFileSystemModel()
        idx = self.model.setRootPath("logs")
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setMinimumSize(600, 600)
        self.tree.setRootIndex(idx)
        self.tree.hideColumn(1)
        self.tree.hideColumn(2)
        self.tree.setColumnWidth(0, 300)
        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(1, QtCore.Qt.SortOrder.DescendingOrder)

        layout = QGridLayout()
        layout.addWidget(self.tree, 0, 0)
        self.setLayout(layout)
