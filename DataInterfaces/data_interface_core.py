"""
Base data interface
"""


class DataInterfaceCore(object):
    def __init__(self):
        self.data_dictionary = {}

    def spin(self):
        pass

    def getDataDictionary(self):
        return self.data_dictionary
