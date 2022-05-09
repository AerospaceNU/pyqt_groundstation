"""
Displays pyro continuity
"""

import PyQt5.QtCore as QtCore

from PyQt5.QtWidgets import QLabel, QGridLayout

from data_helpers import get_value_from_dictionary
from constants import Constants

from Widgets.custom_q_widget_base import CustomQWidgetBase

from pyqtgraph.Qt import QtGui

import pyqtgraph.opengl as gl
import pyqtgraph as pqg
from stl import mesh
import numpy as np

class ThreeDDisplay(CustomQWidgetBase):
    def __init__(self, parent_widget=None):
        super().__init__(parent_widget)

        self.title = "3d Display"
        self.currentSTL = None
        self.axis = [0,0,1]
        self.angle = 0

        layout = QGridLayout()

        self.titleWidget = QLabel()
        self.titleWidget.setText(self.title)
        self.titleWidget.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        layout.addWidget(self.titleWidget, 0, 0, 1, 1)

        self.viewer = gl.GLViewWidget()
        self.viewer.setMinimumWidth(600)
        self.viewer.setMinimumHeight(600)
        # self.viewer.setBackgroundColor(pqg.mkColor('g'))
        layout.addWidget(self.viewer, 1, 0, 1, 1)
        
        self.viewer.setWindowTitle('STL Viewer')
        self.viewer.setCameraPosition(distance=10)
        
        g = gl.GLGridItem()
        g.setSize(200, 200)
        g.setSpacing(5, 5)
        self.viewer.addItem(g)

        self.setLayout(layout)

        self.showSTL("Rocket.stl")

    def updateData(self, vehicle_data, updated_data):
        q = get_value_from_dictionary(vehicle_data, Constants.orientation_quaternion_key, [1,0,0,0])

        self.currentSTL.resetTransform()
        tr = pqg.Transform3D()
        tr.scale(0.1, 0.1, 0.1)
        # tr.translate(0,0,-50)
        tr.rotate(QtGui.QQuaternion(q[0], q[1], q[2], q[3]))
        self.currentSTL.applyTransform(tr, local=True)


    def setWidgetColors(self, widget_background_string, text_string, header_text_string, border_string):
        self.setStyleSheet("QWidget#" + self.objectName() + " {" + widget_background_string + text_string + border_string + "}")
        self.titleWidget.setStyleSheet(widget_background_string + header_text_string)


    def showSTL(self, filename):
        if self.currentSTL:
            self.viewer.removeItem(self.currentSTL)

        points, faces = self.loadSTL(filename)
        meshdata = gl.MeshData(vertexes=points, faces=faces)
        mesh = gl.GLMeshItem(meshdata=meshdata, smooth=True, drawFaces=True, drawEdges=True, edgeColor=(0, 0, 0.5, 0.1))
        self.viewer.addItem(mesh)
        
        self.currentSTL = mesh

    def loadSTL(self, filename):
        m = mesh.Mesh.from_file(filename)
        shape = m.points.shape
        points = m.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)
        return points, faces
