"""
Displays pyro continuity
"""

import math

import numpy as np
import PyQt5.QtCore as QtCore
import pyqtgraph as pqg
import pyqtgraph.opengl as gl
from PyQt5.QtGui import QVector3D
from PyQt5.QtWidgets import QGridLayout, QLabel
from pyqtgraph.Qt import QtGui
from stl import mesh

from src.constants import Constants
from src.data_helpers import euler_to_quaternion, get_value_from_dictionary
from src.Widgets.custom_q_widget_base import CustomQWidgetBase


class ThreeDDisplay(CustomQWidgetBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.title = "3d Display"
        self.currentSTL = None
        self.axis = [0, 0, 1]
        self.angle = 0

        self.scale_factor = 0.1

        layout = QGridLayout()

        self.titleWidget = QLabel()
        self.titleWidget.setText(self.title)
        self.titleWidget.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.titleWidget.setMaximumHeight(self.titleWidget.fontInfo().pixelSize() * 1.5)
        layout.addWidget(self.titleWidget, 0, 0, 1, 1)

        self.viewer = gl.GLViewWidget()
        # self.viewer.setMinimumWidth(600)
        # self.viewer.setMinimumHeight(600)
        # self.viewer.setBackgroundColor(pqg.mkColor('g'))
        layout.addWidget(self.viewer, 1, 0, 1, 1)
        # layout.setRowMinimumHeight(1, 600)
        # layout.setColumnMinimumWidth(0, 600)

        self.viewer.setWindowTitle("STL Viewer")
        self.viewer.setCameraPosition(distance=10)

        self.orientation_quaternion = [1, 0, 0, 0]
        self.altitude = 0

        g = gl.GLGridItem()
        g.setSize(200, 200)
        g.setSpacing(5, 5)
        self.viewer.addItem(g)

        self.setLayout(layout)

        self.showSTL("src/Assets/Rocket.stl")

    def customUpdateAfterThemeSet(self):
        self.viewer.setBackgroundColor(self.palette().color(self.backgroundRole()))

    def updateData(self, vehicle_data, updated_data):
        self.orientation_quaternion = get_value_from_dictionary(vehicle_data, Constants.orientation_quaternion_key, [1, 0, 0, 0])
        self.altitude = get_value_from_dictionary(vehicle_data, Constants.altitude_key, 0)

    def updateInFocus(self):
        """We do the rendering in updateInFocus instead of updateData so that it only happens when we're looking at the widget"""
        self.currentSTL.resetTransform()
        tr = pqg.Transform3D()
        tr.scale(self.scale_factor, self.scale_factor, self.scale_factor)
        tr.translate(0, 0, self.altitude / self.scale_factor)

        position = QVector3D(0, 0, self.altitude)

        rotation_quaternion = euler_to_quaternion(0, math.radians(90), 0)

        self.viewer.setCameraPosition(pos=position)
        tr.rotate(QtGui.QQuaternion(self.orientation_quaternion[0], self.orientation_quaternion[1], self.orientation_quaternion[2], self.orientation_quaternion[3]))
        tr.rotate(QtGui.QQuaternion(rotation_quaternion[0], rotation_quaternion[1], rotation_quaternion[2], rotation_quaternion[3]))
        self.currentSTL.applyTransform(tr, local=True)

    def showSTL(self, filename):
        if self.currentSTL:
            self.viewer.removeItem(self.currentSTL)

        points, faces = self.loadSTL(filename)
        meshdata = gl.MeshData(vertexes=points, faces=faces)
        mesh = gl.GLMeshItem(meshdata=meshdata, smooth=True, drawFaces=True, drawEdges=False, edgeColor=(0, 0, 0.5, 0.1), shader="shaded")
        self.viewer.addItem(mesh)

        self.currentSTL = mesh

    def loadSTL(self, filename):
        m = mesh.Mesh.from_file(filename)
        points = m.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)
        return points, faces
