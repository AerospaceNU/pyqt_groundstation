"""
Holds a list of strings and does some automatic formatting
"""

import time

from src.callback_handler import CallbackHandler


class CommsConsoleHelper(object):
    def __init__(self, callback, max_length=30):
        self.command_history_list = []

        self.callbackHandler = CallbackHandler()
        self.callback = callback

        self.addNewEntryNextTime = True
        self.maxLength = max_length

    def manualAddEntry(self, text: str, from_remote=False):
        self.addEntry(text, from_remote)
        self.addNewEntryNextTime = True

        self.queueCallback()

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

        self.queueCallback()

    def addEntry(self, text, from_remote):
        text = text.strip("\n")

        if from_remote:
            self.command_history_list.append("{0}: {1}".format(time.strftime("%H:%M:%S"), text))
        else:
            self.command_history_list.append("{0}: > {1}".format(time.strftime("%H:%M:%S"), text))

        # Limit length of command_history_list
        self.command_history_list = self.command_history_list[-self.maxLength:]

    def addToLastEntry(self, text, from_remote=False):
        if len(self.command_history_list) > 0:
            self.command_history_list[-1] += text
        else:
            self.addEntry(text, from_remote)

    def queueCallback(self):
        # Request a new callback with the new data
        if self.addNewEntryNextTime:
            self.callbackHandler.requestCallback(self.callback, str(self.command_history_list[-1]).strip())

    def getList(self):
        return self.command_history_list
