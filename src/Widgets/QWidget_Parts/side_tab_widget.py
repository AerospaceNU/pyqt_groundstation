from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QWidget, QStackedWidget, QPushButton, QFrame, QScrollArea, QSizePolicy


class SideTabWidget(QWidget):
    def __init__(self):
        super(SideTabWidget, self).__init__()

        self.button_widget = QWidget()
        self.button_layout = QVBoxLayout()
        self.button_widget.setLayout(self.button_layout)
        self.button_widget.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setContentsMargins(0, 1, 0, 1)
        self.button_widget.setMinimumWidth(200)
        self.button_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum)

        self.button_scroll_area = QScrollArea()
        self.button_scroll_area.horizontalScrollBar().setEnabled(False)
        self.button_scroll_area.setWidget(self.button_widget)
        self.button_scroll_area.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout = QGridLayout()
        main_layout.addWidget(self.button_scroll_area, 0, 0)
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
        self.button_widget.adjustSize()
        self.button_scroll_area.adjustSize()

    def goToTabByName(self, name):
        index = self.tab_names.index(name)
        self.goToTabByIndex(index)

    def goToTabByIndex(self, index):
        self.stacked_widget.setCurrentIndex(index)
