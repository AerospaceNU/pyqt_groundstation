"""
Text box widget
"""

from PyQt5.QtWidgets import QGridLayout, QWidget, QScrollArea

from src.Widgets import custom_q_widget_base
from src.Widgets.QWidget_Parts.reconfigure_line_holder import ReconfigureLineDescription
from src.Widgets.QWidget_Parts.settings_section import SettingsSection

from src.data_helpers import get_text_from_qcolor


class SettingsManager(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.scrollArea = QScrollArea()
        self.scrollPage = QWidget()
        self.subLayout = QGridLayout()

        self.setLayout(QGridLayout())
        self.layout().addWidget(self.scrollArea)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.scrollArea.setWidget(self.scrollPage)
        self.scrollPage.setLayout(self.subLayout)

        self.iniData = {}
        self.settingsSections = []

    def refresh(self):
        sections = self.widgetSettings.getSections()
        sections.sort()
        if sections != list(self.iniData.keys()):
            for section in sections:
                section_data = self.widgetSettings.getSectionData(section)
                self.iniData[section] = section_data.copy()

            # If there's the wrong number of items, adjust the widget
            while len(self.iniData.keys()) > len(self.settingsSections):
                line = SettingsSection()
                line.adjustSize()
                line.addCallback(self.textEntryCallback)
                self.subLayout.addWidget(line)
                self.settingsSections.append(line)
            while len(self.iniData.keys()) < len(self.settingsSections):
                self.subLayout.removeWidget(self.reconfigureLines[-1])
                self.reconfigureLines[-1].deleteLater()
                del self.reconfigureLines[-1]

            for i in range(len(self.iniData)):
                section_name = list(self.iniData.keys())[i]
                self.settingsSections[i].setName(section_name)

                lines = []
                section_data = self.iniData[section_name]
                for key in section_data:
                    lines.append(ReconfigureLineDescription(name=key, type="string", value=section_data[key], description_text="", enum_options=[]))

                self.settingsSections[i].setLineOptions(lines)

        self.scrollPage.adjustSize()
        self.updateAfterThemeSet()

    def textEntryCallback(self, section, key, value):
        self.widgetSettings.save(key, value, section=section)

    def updateData(self, vehicle_data, updated_data):
        self.refresh()

    def customUpdateAfterThemeSet(self):
        text_color = get_text_from_qcolor(self.palette().text().color())

        for panel in self.settingsSections:
            panel.titleBox.setStyleSheet("font: 14pt Arial; color: {}".format(text_color))
