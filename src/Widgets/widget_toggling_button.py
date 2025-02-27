# from PyQt5.QtWidgets import QPushButton
# from PyQt5.QtCore import pyqtSignal

# class ToggleButtonWidget(QPushButton):
#     toggled = pyqtSignal(bool)  # Signal to notify when toggled

#     def __init__(self, parent=None):
#         super().__init__("On", parent)
#         self.is_enabled = True  # Default state
#         self.setFixedSize(50, 20)  # Small button
#         self.setStyleSheet("font-size: 10px; padding: 2px;")
#         self.clicked.connect(self.toggleState)
#         self.updateStyle()

#     def toggleState(self):
#         """Toggle state and emit signal."""
#         self.is_enabled = not self.is_enabled
#         self.setText("On" if not self.is_enabled else "Off")
#         self.updateStyle()
#         self.toggled.emit(self.is_enabled)  # Notify parent widget

#     def updateStyle(self):
#         """Change button color based on state."""
#         if self.is_enabled:
#             self.setStyleSheet("background-color: red; color: white; font-weight: bold; font-size: 10px; padding: 2px;")
#         else:
#             self.setStyleSheet("background-color: green; color: white; font-weight: bold; font-size: 10px; padding: 2px;")
