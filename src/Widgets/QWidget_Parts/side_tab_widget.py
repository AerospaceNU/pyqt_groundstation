from PyQt5.QtWidgets import QComboBox, QGridLayout, QLabel, QLineEdit, QWidget, QStackedWidget, QPushButton, QFrame


class SideTabWidget(QWidget):
    def __init__(self):
        super(SideTabWidget, self).__init__()

        self.stacked_widget = QStackedWidget()
        button_widget = QFrame()
        self.button_layout = QGridLayout()
        button_widget.setLayout(self.button_layout)

        main_layout = QGridLayout()
        main_layout.addWidget(button_widget, 0, 0)
        main_layout.addWidget(self.stacked_widget, 0, 1)
        main_layout.setContentsMargins(1, 1, 1, 1)
        self.setLayout(main_layout)

        self.tab_names = []

    def addTab(self, tab_name: str, tab_widget: QWidget):
        button = QPushButton()
        button.setText(tab_name)
        button.clicked.connect(lambda: self.goToTabByName(tab_name))

        self.stacked_widget.addWidget(tab_widget)
        self.button_layout.addWidget(button)
        self.tab_names.append(tab_name)

    def goToTabByName(self, name):
        index = self.tab_names.index(name)
        self.goToTabByIndex(index)

    def goToTabByIndex(self, index):
        self.stacked_widget.setCurrentIndex(index)
