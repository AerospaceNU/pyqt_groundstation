"""
Tab that has all the prop stuff

"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QScrollArea, QSizePolicy, QWidget

from src.Widgets.annunciator_panel import AnnunciatorPanel
from src.Widgets.MainTabs.main_tab_common import TabCommon
from src.Widgets.prop_control_widget import PropControlWidget
from src.Widgets.prop_sequencer_widget import PropSequencerWidget
from src.Widgets.simple_console_widget import SimpleConsoleWidget
from src.Widgets.text_box_drop_down_widget import TextBoxDropDownWidget


class PropViewTab(TabCommon):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = QGridLayout()
        self.setLayout(layout)

        prop_control_widget = self.addWidget(PropControlWidget())
        text_box_widget = self.addWidget(TextBoxDropDownWidget())  # (auto_size=False, round_to_decimals=3))
        console = self.addWidget(SimpleConsoleWidget())
        sequencer = self.addWidget(PropSequencerWidget())

        text_box_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        text_box_widget.setMaximumWidth(1500)
        console.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        console.setMinimumHeight(200)

        # We need a baby layout within which to put scrollable widgets

        scroll_area = QScrollArea()  # Scroll Area which contains the widgets, set as the centralWidget
        scroll_widget = QWidget()  # Widget that contains the collection of Vertical Box
        scrolling_vbox = QGridLayout()  # The Vertical Box that contains the Horizontal Boxes of  labels and buttons

        scroll_widget.setLayout(scrolling_vbox)

        # Scroll Area Properties
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)

        prop_control_widget.setMinimumWidth(1100)
        prop_control_widget.setMinimumHeight(600)
        scrolling_vbox.addWidget(prop_control_widget, 0, 0, 1, 2, Qt.AlignCenter)

        sequencer.setMinimumWidth(550)
        sequencer.setMaximumHeight(250)
        scrolling_vbox.addWidget(sequencer, 1, 0, 1, 1, Qt.AlignRight)

        # redlines
        scrolling_vbox.addWidget(self.addWidget(AnnunciatorPanel()), 1, 1, 1, 1, Qt.AlignCenter)
        # no data
        text_box_widget.setMinimumWidth(500)
        text_box_widget.setMaximumWidth(700)
        text_box_widget.setMinimumHeight(500)
        text_box_widget.setMaximumHeight(600)

        scrolling_vbox.addWidget(text_box_widget, 0, 2, 1, 1)
        # messages from stand
        console.setMaximumHeight(240)
        # console.setMinimumWidth(650)
        console.setMaximumWidth(700)
        scrolling_vbox.addWidget(console, 1, 2, 1, 1)

        layout.addWidget(scroll_area, 0, 0)

        # HACK!! Set the left scrolling area's width to the min size of the component plus some padding
        scroll_area.setMinimumWidth(scrolling_vbox.minimumSize().width() + 150)


if __name__ == "__main__":

    from PyQt5.QtWidgets import QApplication, QMainWindow

    application = QApplication([])  # PyQt Application object
    mainWindow = QMainWindow()  # PyQt MainWindow widget

    navball = PropViewTab()

    mainWindow.setCentralWidget(navball)
    mainWindow.show()

    from qt_material import apply_stylesheet

    apply_stylesheet(application, theme="themes/High Contrast Light.xml")
    navball.customUpdateAfterThemeSet()

    application.exec_()
