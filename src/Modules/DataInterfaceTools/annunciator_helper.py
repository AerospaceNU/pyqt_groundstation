"""
Class to create the data structure to drive an annunciator panel
"""


class AnnunciatorHelper(object):
    def __init__(self):
        self.annunciator_list = []

    def setAnnunciator(self, index, name, level, message):
        data = [name, level, message]

        while len(self.annunciator_list) < index + 1:
            self.annunciator_list.append([" ", 0, " "])

        self.annunciator_list[index] = data

    def getList(self):
        return self.annunciator_list

    def getOverallStatus(self):
        overall_status = 0

        for annunciator in self.annunciator_list:
            overall_status = max(overall_status, annunciator[1])

        return overall_status
