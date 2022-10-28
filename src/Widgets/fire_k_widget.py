"""
Calculates if we have enough K in the bottle to fire
"""

import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit, QPushButton

from src.Widgets.custom_q_widget_base import CustomQWidgetBase


class FireKWidget(CustomQWidgetBase):
    def __init__(self, parent_widget=None):
        super().__init__(parent_widget)

        self.xBuffer = 0
        self.yBuffer = 0
        MIN_WIDTH = 200

        """

        ------------------------- Fire K? ----------------------- (2 cols)
        Pressurant Bottle Volume (SCF):                 [      ]
        Current Pressurant Bottle Pressure (psig):      [      ]
        Fire Time:                                      [      ]
        Fuel Ullage Volume (L):                         [      ]
        LOX Ullage Volume (L):                          [      ]
                                                        [ Calc ]
        """

        self.title = "Fire K?"
        # Store user input
        self.inputs = {"Pressurant Bottle Volume (SCF)": "", "Current Pressurant Bottle Pressure (psig)": "", "Fire Time": "", "Fuel Ullage Volume (L)": "", "LOX Ullage Volume (L)": ""}
        # Store answer to function
        self.answer = False

        layout = QGridLayout()
        self.titleWidget = QLabel()
        self.titleWidget.setText(self.title)
        self.titleWidget.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        layout.addWidget(self.titleWidget, 0, 0, 1, 2)

        index = 0
        for label, storedValue in self.inputs.items():
            qlabel = QLabel()
            qlabel.setText(f"{label}:")

            textArea = QLineEdit()
            textArea.setText(storedValue)
            textArea.setMinimumWidth(MIN_WIDTH)
            textArea.textChanged.connect(lambda newText, label=label: self.textChangedHandler(label, newText))

            layout.addWidget(qlabel, index + 1, 0, 1, 1)
            layout.addWidget(textArea, index + 1, 1, 1, 1)
            index += 1

        self.answerLabel = QLabel()
        self.answerLabel.setText("Answer: None")
        layout.addWidget(self.answerLabel, index + 2, 1, 1, 1)

        self.calcButton = QPushButton()
        self.calcButton.setText("Calculate")
        self.calcButton.clicked.connect(self.calculateHandler)
        layout.addWidget(self.calcButton, index + 2, 0, 1, 1)

        self.setLayout(layout)

    # Save the user's input
    def textChangedHandler(self, label, value):
        self.inputs[label] = value

    # When button is pressed, run the calculation
    def calculateHandler(self):
        input_bot_SCF = int(self.inputs["Pressurant Bottle Volume (SCF)"])
        input_cur_bottle_pressure = int(self.inputs["Current Pressurant Bottle Pressure (psig)"])
        input_dt = int(self.inputs["Fire Time"])
        input_fuel_ullage = int(self.inputs["Fuel Ullage Volume (L)"])
        input_lox_ullage = int(self.inputs["LOX Ullage Volume (L)"])

        needed_vol_actual_vol = self.doWeHaveEnoughKInTheBottle(input_bot_SCF, input_cur_bottle_pressure, input_dt, input_fuel_ullage, input_lox_ullage)
        needed_vol = needed_vol_actual_vol[0]
        actual_vol = needed_vol_actual_vol[1]

        self.answer = actual_vol >= needed_vol
        answerText = "YES" if self.answer else "NO"
        self.answerLabel.setText(f"Answer: {answerText}\nActual (L): {(round(actual_vol, 3))}\tNeeded (L): {(round(needed_vol, 3))}")

    def doWeHaveEnoughKInTheBottle(self, bot_SCF, current_bottle_pressure, dt, fuel_ullage, lox_ullage):
        R_mol = 8314
        psi_Pa = 6894.76
        m3_L = 1000
        SCF_L = 28.3168

        # Selected Values (General)
        P_gas0 = current_bottle_pressure * psi_Pa
        ullage_fuel = fuel_ullage / m3_L
        ullage_ox = lox_ullage / m3_L

        V_kBot = bot_SCF * SCF_L / (2214.7 / 14.7)

        # Selected Values (Fuel) - most values for fuel and oxidizer and fuel are same and are established here
        mdot_fuel = 0.5130783892
        rho_fuel = 798
        k_gasF = 1.4
        M_gasF = 28.0134
        P_fuel = 850 * psi_Pa
        P_regF = P_fuel
        P_gasF = 850 * psi_Pa
        T_gasF0 = 298
        Fact_fuel_ull = 1.05
        Fact_gasF_res = 1.05

        # Selected Values (Oxidizer) CHECK OURO
        mdot_ox = 0.8209254226
        rho_ox = 1140.7
        k_gasO = k_gasF
        M_gasO = M_gasF
        P_ox = 750 * psi_Pa
        P_regO = P_ox
        P_gasO = 850 * psi_Pa
        T_gasO0 = 298
        Fact_ox_ull = 1.05
        Fact_gasO_res = 2

        # Calculations (Fuel)
        V_fuel = mdot_fuel * dt * Fact_fuel_ull / rho_fuel + ullage_fuel

        R_gasF = R_mol / M_gasF

        m_gasF0 = (P_regF * V_fuel) / (R_gasF * T_gasF0) * (k_gasF / (1 - (P_gasF / P_gas0)))

        V_gasF0 = ((m_gasF0 * Fact_gasF_res) * R_gasF * T_gasF0) / P_gas0

        # Calculations (Ox)
        V_ox = mdot_ox * dt * Fact_ox_ull / rho_ox + ullage_ox

        R_gasO = R_mol / M_gasO

        m_gasO0 = (P_regO * V_ox) / (R_gasO * T_gasO0) * (k_gasO / (1 - (P_gasO / P_gas0)))

        V_gasO0 = ((m_gasO0 * Fact_gasO_res) * R_gasO * T_gasO0) / P_gas0

        # Display

        needed_vol = (V_gasF0 + V_gasO0) * m3_L  # Needed Bottle Volume (L)
        actual_vol = V_kBot  # Actual Bottle Volume (L)
        return needed_vol, actual_vol
