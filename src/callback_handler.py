"""
Class that handles callbacks across the GUI

Exploits class variables so that you can make as many instances of this as you want, and they will all share the same queue and callback list.
Just don't call processCallbacks anywhere other than the main loop.
"""

import copy
from typing import List


class CallbackHandler(object):
    # Having these as class variables means they're shared across objects
    callback_functions = {}  # Dictionary of list of callback functions that can be called from any widget.  These are typically added by modules.  {callback_name: [function_pointer, pointer, ...], ...}
    callback_queue = []  # List of callback function names to call.  These are called in the GUI thread during the update() function

    def __init__(self):
        self.own_callback_fns = {}

    def __del__(self):
        self.closeOut()

    def closeOut(self):
        """
        Need to delete references to callbacks we've added when we're deleted so that there aren't still references to whatever part of the GUI added those callbacks
        That way whatever added those callbacks can be safely deleted also
        """

        for callback in self.own_callback_fns:
            index = self.own_callback_fns[callback]
            self.callback_functions[callback][index] = None

    def requestCallback(self, callback_name: str, data):
        self.callback_queue += [[callback_name, data]]

    def requestMultipleCallbacks(self, callbacks: List):
        self.callback_queue += callbacks

    def processCallbacks(self):
        callbacks = copy.deepcopy(self.callback_queue)
        self.callback_queue.clear()

        for callback_data in callbacks:
            callback_name = callback_data[0]
            if callback_name in self.callback_functions:
                # print("Processing callback {}".format(callback_name))
                callback_list = self.callback_functions[callback_name]
                for callback_function in callback_list:
                    if callback_function is not None:
                        try:
                            callback_function(callback_data[1])  # <sarcasm>What amazingly clean code</sarcasm>
                        except Exception as e:
                            print("Unable to call callback {0}: [{1}]".format(callback_name, e))
            else:
                pass
                # print("{} isn't a valid callback".format(callback_data[0]))  # Debugging code
                # print(callback_name, callback_data[1])
                # print(list(self.callback_functions.keys()))

    def addCallback(self, target: str, callback: callable):
        if target not in self.callback_functions:
            self.callback_functions[target] = []

        self.callback_functions[target].append(callback)
        self.own_callback_fns[target] = len(self.callback_functions[target]) - 1

    def getAvailableCallbacks(self) -> list:
        return list(self.callback_functions.keys())
