"""
Text box widget
"""
from PyQt5 import QtCore
from PyQt5.QtWidgets import QComboBox, QGridLayout, QLabel, QPushButton, QWidget, QSlider, QLineEdit 

from src.constants import Constants
from src.data_helpers import get_value_from_dictionary
from src.Widgets import custom_q_widget_base
from src.Widgets.QWidget_Parts import sideways_bar_graph


class MotorControl(custom_q_widget_base.CustomQWidgetBase):
    def __init__(self, parent_widget: QWidget = None):
        super().__init__(parent_widget)

        self.cutter_enabled = False
        self.cutter_armed = False


        self.slider_values = [0, 0]
        self.motor_sliders = [QSlider() for _ in range(2)]
        for i, slider in enumerate(self.motor_sliders):
            slider.setOrientation(QtCore.Qt.Orientation.Vertical)
            slider.setRange(-2000, 2000)
            slider.setValue(0)
        self.motor_sliders[0].valueChanged.connect(lambda value: self.setSliderPosition(0, value))
        self.motor_sliders[1].valueChanged.connect(lambda value: self.setSliderPosition(1, value))
        self.slider_labels = [QLabel() for _ in range(2)]
        self.increment_box = QLineEdit()
        self.increment = 50
        self.increment_box.setText("50")
        self.increment_box.textChanged.connect(self.setIncrement)
        self.degrees_box = [QLineEdit() for _ in range(2)]
        for i, lab in enumerate(self.slider_labels):
            lab.setText(f"Motor {i}:")
            self.degrees_box[i].setText("0")
            self.degrees_box[i].setMaximumWidth(70)
        
        self.degrees_box[0].textChanged.connect(lambda text: self.setSliderPosition(0, text))
        self.degrees_box[1].textChanged.connect(lambda text: self.setSliderPosition(1, text))


        self.increment_label = QLabel()
        self.increment_label.setText("Set Increment:")

        self.title_label = QLabel()
        self.title_label.setText("Dynamixel Motor Control")
        self.set_1_button = QPushButton()
        self.set_1_button.setText("Set Motor 1")
        self.set_2_button = QPushButton()
        self.set_2_button.setText("Set Motor 2")

        self.up_1_button = QPushButton()
        self.up_1_button.setText("Inc")
        self.down_1_button = QPushButton()
        self.down_1_button.setText("Dec")
        self.up_2_button = QPushButton()
        self.up_2_button.setText("Inc")
        self.down_2_button = QPushButton()
        self.down_2_button.setText("Dec")
        self.up_1_button.clicked.connect(lambda _: self.incrementMotor(0))
        self.up_2_button.clicked.connect(lambda _: self.incrementMotor(1))
        self.down_1_button.clicked.connect(lambda _: self.decrementMotor(0))
        self.down_2_button.clicked.connect(lambda _: self.decrementMotor(1))
        self.set_1_button.clicked.connect(lambda _: self.buttonPressed(0))
        self.set_2_button.clicked.connect(lambda _: self.buttonPressed(1))

        layout = QGridLayout()

        data_view_layout = QGridLayout()
        data_view_layout.addWidget(self.title_label, 1, 3)
        data_view_layout.addWidget(self.motor_sliders[0], 2, 1)
        data_view_layout.addWidget(self.slider_labels[0], 2, 2)
        data_view_layout.addWidget(self.degrees_box[0], 3, 2)
        data_view_layout.addWidget(self.motor_sliders[1], 2, 5)
        data_view_layout.addWidget(self.slider_labels[1], 2, 4)
        data_view_layout.addWidget(self.degrees_box[1], 3, 4)
        

        data_view_layout.addWidget(self.increment_label, 4, 3)
        data_view_layout.addWidget(self.up_1_button, 5, 1)
        data_view_layout.addWidget(self.down_1_button, 5, 2)
        data_view_layout.addWidget(self.increment_box, 5, 3)
        data_view_layout.addWidget(self.up_2_button, 5, 4)
        data_view_layout.addWidget(self.down_2_button, 5, 5)
        data_view_layout.addWidget(self.set_1_button, 6, 1)
        data_view_layout.addWidget(self.set_2_button, 6, 3)
        layout.addLayout(data_view_layout, 1, 1)


        self.setLayout(layout)

        # self.state_text_box.setText("State:")
        # self.light_text_box.setText("Light:")
        # self.cut_1_label.setText("Cut 1")
        # self.cut_2_label.setText("Cut 2")
        # self.cutting_enable_button.setText("Enable Commands")
        # self.cut_1_button.setText("Cut Line 1")
        # self.cut_2_button.setText("Cut Line 2")
        # self.arm_button.setText("Arm Line Cutter")

        # self.cut_1_label.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        # self.cut_1_box.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        # self.cut_2_label.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        # self.cut_2_box.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

        self.setMinimumWidth(250)
        # self.state_text_box.setMaximumWidth(50)
        # self.light_text_box.setMaximumWidth(50)

        # self.state_text_box.adjustSize()
        # self.light_text_box.adjustSize()

        # self.cutting_enable_button.clicked.connect(self.onEnableButtonPress)
        # self.cut_1_button.clicked.connect(lambda: self.onCutButtonPressed(1))
        # self.cut_2_button.clicked.connect(lambda: self.onCutButtonPressed(2))
        # self.arm_button.clicked.connect(self.onArmButtonPressed)

    def decrementMotor(self, motor_index):
        self.setSliderPosition(motor_index, self.slider_values[motor_index]-self.increment)

        
    def incrementMotor(self, motor_index):
        self.setSliderPosition(motor_index, self.slider_values[motor_index]+self.increment)


    def setIncrement(self, increment):
        try:
            increment = int(increment)
        except:
            return
        self.increment = increment

    def setSliderPosition(self, slider_index, value):
        try:
            value = int(value)
        except:
            return
        self.slider_values[slider_index] = value
        self.motor_sliders[slider_index].setValue(value)
        self.slider_labels[slider_index].setText(f"Motor {slider_index}")
        self.degrees_box[slider_index].setText(str(value))
        self.update()

    def updateData(self, vehicle_data, updated_data):
        self.update()

    def buttonPressed(self, button_number):
        cmd = f"--motorcontrol -m {button_number} -d {self.slider_values[button_number]}"
        self.callback_handler.requestCallback(Constants.cli_interface_key, cmd)
        self.update()