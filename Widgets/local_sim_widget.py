"""
Displays pyro continuity
"""

import PyQt5.QtCore as QtCore

from PyQt5.QtWidgets import QLabel, QGridLayout, QLineEdit, QPushButton, QFileDialog

import subprocess, psutil

from Widgets.custom_q_widget_base import CustomQWidgetBase
from config import ConfigSaver


class LocalSimWidget(CustomQWidgetBase):
    def __init__(self, parent_widget=None):
        super().__init__(parent_widget)

        self.xBuffer = 0
        self.yBuffer = 0

        self.title = "Local Simulation"
        self.pathNames = ["Executable", "Flight CSV", "External Flash", "Internal Flash"]

        '''
        ---- Local Sim ---- (6 cols)
        Executable:     [     ] [Pick]
        Fight CSV:      [     ] [Pick]
        External Flash: [     ] [Pick]
        Internal Flash: [     ] [Pick]
          [  Go!  ]    [ Kill ]
        '''

        layout = QGridLayout()
        self.titleWidget = QLabel()
        self.titleWidget.setText(self.title)
        self.titleWidget.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        layout.addWidget(self.titleWidget, 0, 0, 1, 6)

        self.titleWidgets = []
        self.paths = []
        self.buttons = []
        self.defaults = ["~/Documents/github/stm32-avionics/build/desktop-simulator/desktop_sim", "~/Downloads/super-guppy-4-2-output-post.csv", "external_flash.dat", "internal_flash.dat"]
        for idx, name in enumerate(self.pathNames):
            label = QLabel()
            label.setText(f"{name}:")
            self.titleWidgets.append(label)

            path = QLineEdit()
            path.setText(self.defaults[idx])
            # path.setMinimumWidth(width)
            self.paths.append(path)
            path.returnPressed.connect(lambda idx=idx: self.savePath(idx))

            button = QPushButton()
            button.clicked.connect(lambda idx=idx, name=name: self.buttonPressHandler(idx, name))
            button.setText("Pick")
            self.buttons.append(button)

            layout.addWidget(label, idx + 1, 0, 1, 2)
            layout.addWidget(path, idx + 1, 2, 1, 2)
            layout.addWidget(button, idx + 1, 4, 1, 2)

        goButton = QPushButton()
        goButton.setText("Launch Sim")
        goButton.clicked.connect(lambda: self.launchSim())
        layout.addWidget(goButton, idx + 2, 0, 1, 3)
        killButton = QPushButton()
        killButton.setText("Kill Sim")
        killButton.clicked.connect(lambda: self.killSim())
        layout.addWidget(killButton, idx + 2, 3, 1, 3)

        self.setLayout(layout)

        self.loadFromConfig()
        self.saveAll()

    def loadFromConfig(self):
        for idx, name in enumerate(self.pathNames):
            oldPath = ConfigSaver.get("SimWidget", name.replace(" ", "_"))
            if oldPath is not None and oldPath != "":
                self.paths[idx].setText(oldPath)
            else:
                self.paths[idx].setText(self.defaults[idx])
            
    def savePath(self, idx):
        ConfigSaver.save("SimWidget", self.pathNames[idx].replace(" ", "_"), self.paths[idx].text())

    def saveAll(self):
        for i in range(len(self.pathNames)):
            self.savePath(i)

    def buttonPressHandler(self, idx: int, name: str):
        file, check = QFileDialog.getOpenFileName(None, f"Select {name}",
                                               "", "All Files (*);;CSV Files (*.csv)")
        if check:
            idx = self.pathNames.index(name)
            self.paths[idx].setText(file)
            self.savePath(idx)

    def launchSim(self):
        self.simProcess = subprocess.Popen(" ".join(map(lambda x: x.text(), self.paths)), shell=True)
        self.saveAll()
        print("Launched sim")
        # TODO have this enable the local simulation data interface

    def killSim(self):
        # process = psutil.Process(self.simProcess)
        # for proc in process.children(recursive=True):
        #     proc.kill()
        # process.kill()
        # self.simProcess.kill()
        import os, signal
        os.kill(self.simProcess.pid, signal.SIGTERM)
        # os.killpg(os.getpgid(self.simProcess.pid), signal.SIGTERM)
        # subprocess.kill(self.simProcess)


    def setWidgetColors(self, widget_background_string, text_string, header_text_string, border_string):
        self.setStyleSheet("QWidget#" + self.objectName() + " {" + widget_background_string + text_string + border_string + "}")
        self.titleWidget.setStyleSheet(widget_background_string + header_text_string)

        for widget in self.titleWidgets:
            widget.setStyleSheet(widget_background_string + text_string)