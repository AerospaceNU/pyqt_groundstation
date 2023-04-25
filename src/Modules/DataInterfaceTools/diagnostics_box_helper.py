"""
Class to contain the data structure for a diagnostics box
"""

from src.constants import Constants


class DiagnosticsBoxHelper(object):
    def __init__(self, source_mame):
        self.diagnostics_dict = {}

        self.source_name = source_mame

    def updatePanel(self, panel_name, panel_dict):
        panel_struct = []
        for line_title in panel_dict:
            panel_struct.append([line_title, panel_dict[line_title]])

        self.diagnostics_dict[panel_name] = panel_struct

    def setPanelStruct(self, panel_name, panel_data):
        self.diagnostics_dict[panel_name] = panel_data

    def getDatabaseDictComponents(self):
        database_dict = {}

        for panel_name in self.diagnostics_dict:
            panel_data = self.diagnostics_dict[panel_name]

            if len(panel_data) > 0:
                database_dict[Constants.makeDiagnosticsKey(self.source_name, panel_name)] = panel_data

        return database_dict
