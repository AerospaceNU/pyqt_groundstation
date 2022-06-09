"""
I literally have no idea what any of the opengl stuff does
"""

import math
import os

import cv2

from OpenGL.GL import *
from OpenGL.GLU import *

from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPolygon, QRegion
from PyQt5.QtWidgets import QOpenGLWidget, QWidget

from src.data_helpers import interpolate, quaternion_to_euler_angle
from src.Widgets.QWidget_Parts.basic_image_display import BasicImageDisplay


class NavballDisplayWidget(QOpenGLWidget):
    def __init__(self, parent_widget: QWidget = None):
        super().__init__(parent_widget)

        self.roll = 0
        self.pitch = 0
        self.yaw = 0

        dir_name = os.path.dirname(__file__)
        dir_name = os.path.abspath(os.path.join(dir_name, "../.."))
        img_data = cv2.imread("{}/Assets/navball.png".format(dir_name), cv2.IMREAD_UNCHANGED)
        img_data = cv2.flip(img_data, 0)  # OpenCV images and OpenGL images are backwards each other
        self.img_data = cv2.cvtColor(img_data, cv2.COLOR_BGR2RGB)

        crossHair = cv2.imread("{}/Assets/cross_hair.png".format(dir_name), cv2.IMREAD_UNCHANGED)
        self.crossHairImage = BasicImageDisplay(crossHair, int(10), parent=self)
        self.crossHairImage.setSingleColor(255, 0, 0)

        self.setSize(800)

    def setSize(self, size):
        self.setMinimumWidth(size)
        self.setMaximumWidth(size)
        self.setMinimumHeight(size)
        self.setMaximumHeight(size)

        self.crossHairImage.setTargetWidth(size * 0.7)

        self.refreshMask()

    def refreshMask(self):
        # Set up circular mask for painter
        num_points = 100
        points = []
        radius = (self.width() / 2.0) * 0.975

        # Make a circle
        for i in range(num_points):
            theta = interpolate(i, 0, num_points, 0, 6.28)
            dx = math.cos(theta) * radius
            dy = math.sin(theta) * radius
            x = self.width() / 2 + dx
            y = self.height() / 2 + dy

            points.append(QPoint(int(x), int(y)))

        poly = QPolygon(points)
        region = QRegion(poly)
        self.setMask(region)

    def setOrientation(self, quaternion):
        [self.roll, self.pitch, self.yaw] = quaternion_to_euler_angle(quaternion)

    def setRPY(self, roll, pitch, yaw):
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw

    def initializeGL(self):
        """Sets up environment, camera position, and lighting"""
        glShadeModel(GL_SMOOTH)
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)

        light_zero_position = [0, 0, 15, 1]
        light_zero_color = [0.8, 1.0, 0.8, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light_zero_position)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_zero_color)
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
        glEnable(GL_LIGHT0)

        glMatrixMode(GL_PROJECTION)
        gluPerspective(40.0, 1.0, 1.0, 40.0)
        glMatrixMode(GL_MODELVIEW)
        gluLookAt(0, 0, 3, 0, 0, 0, 0, 1, 0)  # The third argument is zoom
        glPushMatrix()

    def generateTexture(self):
        """Sends the texture to OpenGL"""
        textID = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, textID)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.img_data.shape[1], self.img_data.shape[0], 0, GL_RGB, GL_UNSIGNED_BYTE, self.img_data)
        return textID

    def paintGL(self):
        # glClear and glPushMatrix start the render cycle
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()

        # Need to fix rotation before applying rpy rotation
        glRotatef(90, 0, 1, 0)
        glRotatef(-90, 1, 0, 0)
        glRotatef(180, 0, 0, 1)

        # Pitch is negative because of how the texture is
        glRotatef(self.roll, 1, 0, 0)
        glRotatef(-self.pitch, 0, 1, 0)
        glRotatef(self.yaw, 0, 0, 1)

        # Call a bunch of OpenGL stuff
        texture_id = self.generateTexture()
        sphere = gluNewQuadric()
        gluQuadricTexture(sphere, GL_TRUE)
        gluQuadricNormals(sphere, GLU_SMOOTH)
        glEnable(GL_TEXTURE_2D)
        gluSphere(sphere, 1, 50, 50)  # Actually draws the sphere

        gluDeleteQuadric(sphere)
        glDisable(GL_TEXTURE_2D)
        glDeleteTextures(int(texture_id))

        # glPopMatrix stops the drawing process
        glPopMatrix()


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication, QMainWindow

    application = QApplication([])  # PyQt Application object
    mainWindow = QMainWindow()  # PyQt MainWindow widget

    navball = NavballDisplayWidget()

    navball.yaw = -90

    mainWindow.setCentralWidget(navball)
    mainWindow.show()

    application.exec_()
