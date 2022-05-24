"""
I literally have no idea what any of the opengl stuff does
"""


import os
import cv2
from PyQt5 import QtGui

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPolygon, QRegion, QOpenGLShader
from PyQt5.QtWidgets import QWidget, QGridLayout, QOpenGLWidget

from OpenGL.GL import *
from OpenGL.GLU import *


def read_texture():
    dir_name = os.path.dirname(__file__)
    dir_name = os.path.abspath(os.path.join(dir_name, "../.."))
    img_data = cv2.imread("{}/Assets/navball.png".format(dir_name), cv2.IMREAD_UNCHANGED)
    img_data = cv2.cvtColor(img_data, cv2.COLOR_BGR2RGB)

    textID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, textID)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img_data.shape[0], img_data.shape[1], 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    return textID


class NavballWidget(QOpenGLWidget):
    def __init__(self, parent_widget: QWidget = None):
        super().__init__(parent_widget)

        self.roll = 0
        self.pitch = 0

        dir_name = os.path.dirname(__file__)
        dir_name = os.path.abspath(os.path.join(dir_name, "../.."))
        self.image = cv2.imread("{}/Assets/navball.png".format(dir_name), cv2.IMREAD_UNCHANGED)

        # self.setMaximumWidth(200)
        # self.setMaximumHeight(200)

    def initializeGL(self):
        glShadeModel(GL_SMOOTH)
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

        lightZeroPosition = [10., 4., 10., 1.]
        lightZeroColor = [0.8, 1.0, 0.8, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, lightZeroPosition)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
        glEnable(GL_LIGHT0)
        glMatrixMode(GL_PROJECTION)
        gluPerspective(40., 1., 1., 40.)
        glMatrixMode(GL_MODELVIEW)
        gluLookAt(0, 0, 10,
                  0, 0, 0,
                  0, 1, 0)
        glPushMatrix()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()

        tex = read_texture()
        qobj = gluNewQuadric()
        gluQuadricTexture(qobj, GL_TRUE)
        glEnable(GL_TEXTURE_2D)
        gluSphere(qobj, 1, 50, 50)
        gluDeleteQuadric(qobj)
        glDisable(GL_TEXTURE_2D)

        glPopMatrix()


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow

    application = QApplication([])  # PyQt Application object
    mainWindow = QMainWindow()  # PyQt MainWindow widget

    navball = NavballWidget()

    mainWindow.setCentralWidget(navball)
    mainWindow.show()

    application.exec_()
