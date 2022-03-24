"""
Holds a list of strings and does some automatic formatting
"""

import time


class CommsConsoleHelper(object):
    def __init__(self, max_length=10):
        self.command_history_list = []

        self.addNewEntryNextTime = True
        self.maxLength = max_length

    def addEntry(self, text, from_remote=False):
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

    def autoAddEntry(self, text, from_remote=False):
        if self.addNewEntryNextTime:
            self.addEntry(text, from_remote)
        else:
            self.addToLastEntry(text, from_remote)

        if "\n" in text:
            self.addNewEntryNextTime = True
        else:
            self.addNewEntryNextTime = False

    def getList(self):
        return self.command_history_list
