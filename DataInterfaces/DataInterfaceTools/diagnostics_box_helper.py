class DiagnosticsBoxHelper(object):
    def __init__(self):
        self.diagnostics_dict = {}

    def updatePanel(self, panel_name, panel_dict):
        panel_struct = []
        for line_title in panel_dict:
            panel_struct.append([line_title, panel_dict[line_title]])

        self.diagnostics_dict[panel_name] = panel_struct

    def get_diagnostics_dict(self):
        return self.diagnostics_dict
