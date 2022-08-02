"""
Tab that has all the prop stuff

"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QScrollArea, QSizePolicy, QWidget

from src.Widgets.annunciator_panel import AnnunciatorPanel
from src.Widgets.MainTabs.GraphLayouts.prop_stand_graphs import PropStandGraphs
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
        prop_graphs = self.addWidget(PropStandGraphs())
        text_box_widget = self.addWidget(TextBoxDropDownWidget(auto_size=False, round_to_decimals=3))
        console = self.addWidget(SimpleConsoleWidget())
        sequencer = self.addWidget(PropSequencerWidget())

        prop_graphs.layout().setContentsMargins(0, 0, 0, 0)
        text_box_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        text_box_widget.setMaximumWidth(400)
        console.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        console.setMinimumHeight(200)

        # We need a baby layout within which to put scrollable widgets

        scroll_area = QScrollArea()  # Scroll Area which contains the widgets, set as the centralWidget
        scroll_widget = QWidget()  # Widget that contains the collection of Vertical Box
        scrolling_vbox = QGridLayout()  # The Vertical Box that contains the Horizontal Boxes of  labels and buttons

        scroll_widget.setLayout(scrolling_vbox)

        # Scroll Area Properties
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)

        scrolling_vbox.addWidget(prop_control_widget, 0, 0, 1, 2)
        scrolling_vbox.addWidget(sequencer, 1, 0, 1, 1)
        scrolling_vbox.addWidget(self.addWidget(AnnunciatorPanel()), 2, 0, 1, 1)
        scrolling_vbox.addWidget(text_box_widget, 1, 1, 2, 1)
        scrolling_vbox.addWidget(console, 3, 0, 1, 2)

        layout.addWidget(scroll_area, 0, 0)
        layout.addWidget(prop_graphs, 0, 1)

        # HACK!! Set the left scrolling area's width to the min size of the component plus some padding
        scroll_area.setMinimumWidth(scrolling_vbox.minimumSize().width() + 60)
