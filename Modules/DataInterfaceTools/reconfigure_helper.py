"""
Class to contain the data structure for a reconfigure widget
"""


class ReconfigurePage(object):
    def __init__(self, page_name):
        self.reconfigure_lines = []
        self.enum_options = {}
        self.page_name = page_name

        self.callback_dictionary = {}

    def addEnumOption(self, enum_id, description, human_readable_name):
        if enum_id not in self.enum_options:
            self.enum_options[enum_id] = []

        self.enum_options[enum_id].append([description, human_readable_name])

    def updateLine(self, text, line_type, current_value="", description="", config=""):
        found_reconfigure_line = False

        if line_type == "enum" and type(config) == str:
            config = self.enum_options[config]

        for i in range(len(self.reconfigure_lines)):
            line = self.reconfigure_lines[i]

            if len(line) > 0 and line[0] == text:
                if len(self.reconfigure_lines) != 5:
                    self.reconfigure_lines[i] = [text, line_type, current_value, description, config]
                else:
                    self.reconfigure_lines[i][0] = text
                    self.reconfigure_lines[i][1] = line_type
                    if current_value != "": self.reconfigure_lines[i][2] = current_value
                    if description != "": self.reconfigure_lines[i][3] = description
                    if config != "": self.reconfigure_lines[i][4] = config

                found_reconfigure_line = True

        if not found_reconfigure_line:
            self.reconfigure_lines.append([text, line_type, current_value, description, config])

    def bindCallback(self, line_name, function):
        if line_name not in self.callback_dictionary:
            self.callback_dictionary[line_name] = []

        self.callback_dictionary[line_name].append(function)

    def getDataStructure(self):
        return self.reconfigure_lines

    def getPageName(self):
        return self.page_name

    def getCallbackFunctions(self, database_dictionary_key):
        return {"{}_reset".format(database_dictionary_key): self.onReset, "{}_set_new".format(database_dictionary_key): self.onValueChange}

    def onReset(self, data):
        pass

    def onValueChange(self, data):
        split_data = data.split(":")
        if len(split_data) != 3:
            return

        target_page = split_data[0]
        target_line = split_data[1]
        new_value = split_data[2]

        if target_page != self.page_name:
            return

        if target_line in self.callback_dictionary:
            for callback in self.callback_dictionary[target_line]:
                callback(new_value)
