from PyQt5.QtWidgets import QLabel, QWidget, QGridLayout, QComboBox, QLineEdit


class ReconfigureLine(QWidget):
    def __init__(self):
        super(ReconfigureLine, self).__init__()
        self.textBox = QLabel()
        self.entryBox = QLineEdit()
        self.dropDown = QComboBox()

        layout = QGridLayout()
        layout.addWidget(self.textBox, 0, 0)
        layout.addWidget(self.entryBox, 0, 1)
        layout.addWidget(self.dropDown, 0, 1)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.dropDown.hide()

        self.setContentsMargins(0, 0, 0, 0)

        self.callback = None

        self.value = ""
        self.type = ""
        self.description = ""
        self.config = ""
        self.currentIndex = -1

        self.widgetBackgroundString = ""
        self.textString = ""

        self.enumNames = []
        self.enumValues = []

        self.entryBox.returnPressed.connect(self.runCallback)

    def setText(self, text):
        self.textBox.setText(text)

    def setType(self, lineType):
        if lineType != self.type:
            if lineType == "enum":
                self.dropDown.show()
                self.dropDown.setStyleSheet(self.widgetBackgroundString + self.textString)
                self.entryBox.hide()
            else:
                self.dropDown.hide()
                self.entryBox.show()

            self.type = lineType

    def setValue(self, value, force=False):
        value = str(value)

        if value != self.value or force:
            self.entryBox.setText(value)
            if self.type == "enum":
                if value in self.enumValues:
                    index = self.enumValues.index(value)
                    self.dropDown.setCurrentIndex(index)
                    self.currentIndex = index

            self.value = value

    def setDescription(self, description):
        self.description = description
        self.textBox.setToolTip(self.description)
        self.textBox.setToolTipDuration(5000)

    def setConfig(self, config, force=False):
        if config != self.config or force:
            self.enumNames = []
            self.enumValues = []

            if self.type == "enum":
                for i in range(len(config)):
                    item = config[i]
                    self.enumNames.append(item[0])
                    self.enumValues.append(item[1])
                    self.dropDown.clear()
                    self.dropDown.addItems(self.enumNames)

            self.config = config

    def update(self):
        if self.type == "enum":
            if self.dropDown.currentIndex() != self.currentIndex:
                index = self.dropDown.currentIndex()
                self.callback(self.textBox.text(), self.enumValues[index])
                self.currentIndex = index

    def setCallback(self, function):
        self.callback = function

    def runCallback(self):
        if self.callback is not None:
            self.callback(self.textBox.text(), self.entryBox.text())

    def setColor(self, background, border, text):
        self.widgetBackgroundString = background
        self.textString = text

        self.entryBox.setStyleSheet(background + border + text)
        self.dropDown.setStyleSheet(background + text)
        self.textBox.setStyleSheet(background + border + text)
