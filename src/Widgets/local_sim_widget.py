"""
Displays pyro continuity
"""

import os
import platform
import subprocess

import psutil
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import QFileDialog, QGridLayout, QLabel, QLineEdit, QPushButton

from src.Widgets.custom_q_widget_base import CustomQWidgetBase


class LocalSimWidget(CustomQWidgetBase):
    def __init__(self, parent_widget=None):
        super().__init__(parent_widget)

        self.xBuffer = 0
        self.yBuffer = 0
        MIN_WIDTH = 200

        self.title = "Local Simulation"
        self.pathNames = [
            "Executable",
            "Flight CSV",
            "External Flash",
            "Internal Flash",
        ]

        """
        ---- Local Sim ---- (6 cols)
        Executable:     [     ] [Pick]
        Fight CSV:      [     ] [Pick]
        External Flash: [     ] [Pick]
        Internal Flash: [     ] [Pick]
          [  Go!  ]    [ Kill ]
        """

        layout = QGridLayout()
        self.titleWidget = QLabel()
        self.titleWidget.setText(self.title)
        self.titleWidget.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        layout.addWidget(self.titleWidget, 0, 0, 1, 6)

        self.titleWidgets = []
        self.paths = []
        self.buttons = []
        self.defaults = [
            "~/Documents/github/stm32-avionics/build/desktop-simulator/desktop_sim",
            "~/Downloads/super-guppy-4-2-output-post.csv",
            "external_flash.dat",
            "internal_flash.dat",
        ]
        for idx, name in enumerate(self.pathNames):
            label = QLabel()
            label.setText(f"{name}:")
            self.titleWidgets.append(label)

            path = QLineEdit()
            path.setText(self.defaults[idx])
            path.setMinimumWidth(MIN_WIDTH)
            self.paths.append(path)
            path.returnPressed.connect(lambda idx=idx: self.savePath(idx))

            button = QPushButton()
            button.clicked.connect(lambda idx=idx, name=name: self.buttonPressHandler(idx, name))
            button.setText("Pick")
            self.buttons.append(button)

            layout.addWidget(label, idx + 1, 0, 1, 2)
            layout.addWidget(path, idx + 1, 2, 1, 2)
            layout.addWidget(button, idx + 1, 4, 1, 2)

        self.goButton = QPushButton()
        self.goButton.setText("Launch Sim")
        self.goButton.clicked.connect(lambda: self.launchSim())
        layout.addWidget(self.goButton, idx + 2, 0, 1, 3)
        self.killButton = QPushButton()
        self.killButton.setText("Kill Sim")
        self.killButton.clicked.connect(lambda: self.killSim())
        layout.addWidget(self.killButton, idx + 2, 3, 1, 3)

        self.setLayout(layout)

        self.loadFromConfig()
        self.saveAll()

    def loadFromConfig(self):
        for idx, name in enumerate(self.pathNames):
            oldPath = self.widgetSettings.get(name.replace(" ", "_"))
            if oldPath is not None and oldPath != "":
                self.paths[idx].setText(oldPath)
            else:
                self.paths[idx].setText(self.defaults[idx])

    def savePath(self, idx):
        self.widgetSettings.save(self.pathNames[idx].replace(" ", "_"), self.paths[idx].text())

    def saveAll(self):
        for i in range(len(self.pathNames)):
            self.savePath(i)

    def buttonPressHandler(self, idx: int, name: str):
        file, check = QFileDialog.getOpenFileName(None, f"Select {name}", "", "All Files (*);;CSV Files (*.csv)")
        if check:
            idx = self.pathNames.index(name)
            self.paths[idx].setText(file)
            self.savePath(idx)

    def is_win(self):
        from sys import platform

        return platform == "win32"

    def launchSim(self):
        self.killSim()

        args = []

        if self.is_win():
            is32bit = platform.architecture()[0] == "32bit"
            system32 = os.path.join(os.environ["SystemRoot"], "SysNative" if is32bit else "System32")
            bash = os.path.join(system32, "wsl.exe")
            args.append(bash)

        args += list(map(lambda x: x.text(), self.paths))
        args = " ".join(args)

        self.simProcess = subprocess.Popen(args, shell=True)
        self.saveAll()
        print("Launched sim")
        self.callbackEvents.append(["enable_module", "Local Simulation,True"])

    def killSim(self):
        import signal

        try:
            from sys import platform

            if platform == "win32":
                self.simProcess.send_signal(signal.CTRL_C_EVENT)
            else:
                process = psutil.Process(self.simProcess.pid)
                for proc in process.children(recursive=True):
                    proc.kill()
                process.kill()
        except Exception:
            print("Error killing simulated flight")
