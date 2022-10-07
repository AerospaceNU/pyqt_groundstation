import PyQt5.QtCore as QtCore
import qrcode
from PyQt5 import QtGui
from PyQt5.QtWidgets import QCheckBox, QComboBox, QGridLayout, QLabel

from src.constants import Constants
from src.data_helpers import get_value_from_dictionary
from src.Widgets.custom_q_widget_base import CustomQWidgetBase


# from https://stackoverflow.com/questions/20452486/create-qr-code-in-python-pyqt
class Image(qrcode.image.base.BaseImage):
    def __init__(self, border, width, box_size):
        self.border = border
        self.width = width
        self.box_size = box_size
        size = (width + border * 2) * box_size
        self._image = QtGui.QImage(size, size, QtGui.QImage.Format_RGB16)
        self._image.fill(QtCore.Qt.white)

    def pixmap(self):
        return QtGui.QPixmap.fromImage(self._image)

    def drawrect(self, row, col):
        painter = QtGui.QPainter(self._image)
        painter.fillRect((col + self.border) * self.box_size, (row + self.border) * self.box_size, self.box_size, self.box_size, QtCore.Qt.black)

    def save(self, stream, kind=None):
        pass


class RocketLocationQrCode(CustomQWidgetBase):
    def __init__(self, widget=None):
        super().__init__(widget)
        self.label = QLabel(self)
        self.label2 = QLabel(self)
        layout = QGridLayout(self)
        self.button = QCheckBox(text="Pause updastes")
        self.mode_combo_box = QComboBox()
        self.mode_combo_box.addItems(["Google", "Apple", "Raw"])
        self.update_qr = True
        layout.addWidget(self.button, 0, 0)
        layout.addWidget(self.mode_combo_box, 1, 0)
        layout.addWidget(self.label, 2, 0, 1, 1)
        layout.addWidget(self.label2, 3, 0, 1, 1)

    def setQrText(self, text):
        self.label.setPixmap(qrcode.make(text, image_factory=Image).pixmap())

    def updateData(self, vehicle_data, updated_data):
        if self.button.isChecked():
            return

        latitude = get_value_from_dictionary(vehicle_data, Constants.latitude_key, 0)
        longitude = get_value_from_dictionary(vehicle_data, Constants.longitude_key, 0)
        idx = self.mode_combo_box.currentIndex()

        if idx == 0:
            text = f"https://www.google.com/maps/place/{latitude}+{longitude}"
        elif idx == 1:
            text = f"http://maps.apple.com/?address={latitude},{longitude}"
        else:
            text = f"{latitude},{longitude}"

        self.setQrText(text)
        self.label2.setText(text)


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication, QMainWindow

    application = QApplication([])  # PyQt Application object
    mainWindow = QMainWindow()  # PyQt MainWindow widget

    widget = RocketLocationQrCode()

    mainWindow.setCentralWidget(widget)
    mainWindow.show()

    widget.setQrText("https://google.com")

    from qt_material import apply_stylesheet

    apply_stylesheet(application, theme="themes/old_dark_mode.xml")
    # apply_stylesheet(application, theme="themes/high_contrast_light.xml")
    widget.customUpdateAfterThemeSet()

    application.exec_()
