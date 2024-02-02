from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QComboBox, QLabel, QLineEdit, QHBoxLayout, QPushButton, QApplication)
import sys

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Settings')
        self.setGeometry(100, 100, 400, 200)  # Set initial size and position

        # Main layout
        mainLayout = QVBoxLayout()

        # System dropdown setup
        systemLayout = QHBoxLayout()
        systemLabel = QLabel("System:")
        self.systemDropdown = QComboBox()
        self.systemDropdown.addItems(["ibmq_qasm_simulator", "ibm_sherbrooke", "ibm_algiers"])  # Placeholder items
        systemLayout.addWidget(systemLabel)
        systemLayout.addWidget(self.systemDropdown)

        # Shots input setup
        shotsLayout = QHBoxLayout()
        shotsLabel = QLabel("Shots:")
        self.shotsInput = QLineEdit()
        shotsLayout.addWidget(shotsLabel)
        shotsLayout.addWidget(self.shotsInput)

        # Error Mitigation dropdown setup
        errorMitigationLayout = QHBoxLayout()
        errorMitigationLabel = QLabel("Error Mitigation:")
        self.errorMitigationDropdown = QComboBox()
        self.errorMitigationDropdown.addItems(["Low", "Moderate", "Intense"])
        errorMitigationLayout.addWidget(errorMitigationLabel)
        errorMitigationLayout.addWidget(self.errorMitigationDropdown)

        # Transpilation dropdown setup
        transpilationLayout = QHBoxLayout()
        transpilationLabel = QLabel("Transpilation:")
        self.transpilationDropdown = QComboBox()
        self.transpilationDropdown.addItems(["Low", "Moderate", "Intense"])
        transpilationLayout.addWidget(transpilationLabel)
        transpilationLayout.addWidget(self.transpilationDropdown)

        # Adding layouts to the main layout
        mainLayout.addLayout(systemLayout)
        mainLayout.addLayout(shotsLayout)
        mainLayout.addLayout(errorMitigationLayout)
        mainLayout.addLayout(transpilationLayout)

        # OK and Cancel buttons
        self.buttonsLayout = QHBoxLayout()
        self.okButton = QPushButton("OK")
        self.cancelButton = QPushButton("Cancel")
        self.buttonsLayout.addWidget(self.okButton)
        self.buttonsLayout.addWidget(self.cancelButton)
        mainLayout.addLayout(self.buttonsLayout)

        self.setLayout(mainLayout)

        # Connect buttons
        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

    def getSettings(self):
        # Method to return the current settings
        return {
            "system": self.systemDropdown.currentText(),
            "shots": self.shotsInput.text(),
            "errorMitigation": self.errorMitigationDropdown.currentText(),
            "transpilation": self.transpilationDropdown.currentText(),
        }