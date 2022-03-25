"""
Holds a list of strings and does some automatic formatting
"""

import time


class CommsConsoleHelper(object):
    def __init__(self, max_length=30):
        self.command_history_list = []

        self.addNewEntryNextTime = True
        self.maxLength = max_length

    def manualAddEntry(self, text: str, from_remote=False):
        self.addEntry(text, from_remote)
        self.addNewEntryNextTime = True

    def autoAddEntry(self, text, from_remote=False):
        """Used for the CLI radio messages"""
        if self.addNewEntryNextTime:
            self.addEntry(text, from_remote)
        else:
            self.addToLastEntry(text, from_remote)

        if "\n" in text:
            self.addNewEntryNextTime = True
        else:
            self.addNewEntryNextTime = False

    def addEntry(self, text, from_remote):
        text = text.strip("\n")

        if from_remote:
            self.command_history_list.append("{0}: {1}".format(time.strftime("%H:%M:%S"), text))
        else:
            self.command_history_list.append("{0}: > {1}".format(time.strftime("%H:%M:%S"), text))

        self.command_history_list = self.command_history_list[-self.maxLength:]

    def addToLastEntry(self, text, from_remote=False):
        if len(self.command_history_list) > 0:
            self.command_history_list[-1] += text
        else:
            self.addEntry(text, from_remote)

    def getList(self):
        return self.command_history_list
