from PyQt5.QtWidgets import QLabel


class TwoColumnTextDisplay(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def updateValues(self, column_1: [str], column_2: [str]):
        out_string = ""
        longest_line = 0
        for line in column_1:
            line = str(line).replace("\t", "     ").rstrip()  # Do some formatting to convert tabs to spaces and ditch trailing spaces
            longest_line = max(longest_line, len(line))

        for i in range(len(column_1)):
            column_1_text = column_1[i]
            spaces = " " * (longest_line - len(column_1_text) + 2)  # Add two extra spaces to everything
            new_line = "{0}{2}{1}\n".format(column_1_text, str(column_2[i]).lstrip(), spaces)

            out_string = out_string + new_line

        out_string = out_string[:-1]  # Remove last character

        self.setText(out_string)
        self.adjustSize()

    def updateValuesLineList(self, line_list: [[str, str]]):
        column_1 = []
        column_2 = []

        for line in line_list:
            column_1.append(line[0])
            column_2.append(line[1])

        self.updateValues(column_1, column_2)
