import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QDialog)
from PyQt5.QtGui import QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np

from qiskit.providers.basic_provider import BasicProvider
from qiskit import transpile
from qiskit.circuit import QuantumCircuit
from qiskit.visualization import plot_histogram
from qiskit import QuantumCircuit
from qiskit.circuit.library import GroverOperator, MCMT, ZGate
from qiskit.visualization import plot_distribution

def grover_oracle(marked_states):
    """Build a Grover oracle for multiple marked states

    Here we assume all input marked states have the same number of bits

    Parameters:
        marked_states (str or list): Marked states of oracle

    Returns:
        QuantumCircuit: Quantum circuit representing Grover oracle
    """
    if not isinstance(marked_states, list):
        marked_states = [marked_states]
    # Compute the number of qubits in circuit
    num_qubits = len(marked_states[0])

    qc = QuantumCircuit(num_qubits)
    # Mark each target state in the input list
    for target in marked_states:
        # Flip target bit-string to match Qiskit bit-ordering
        rev_target = target[::-1]
        # Find the indices of all the '0' elements in bit-string
        zero_inds = [ind for ind in range(num_qubits) if rev_target.startswith("0", ind)]
        # Add a multi-controlled Z-gate with pre- and post-applied X-gates (open-controls)
        # where the target bit-string has a '0' entry
        qc.x(zero_inds)
        qc.compose(MCMT(ZGate(), num_qubits - 1, 1), inplace=True)
        qc.x(zero_inds)
    return qc

def apply_diffusion(circuit, nqubits):
    # Apply the Grover diffusion operator
    circuit.h(range(nqubits))
    circuit.x(range(nqubits))
    # Apply multi-controlled Z gate
    circuit.h(nqubits - 1)
    circuit.mct(list(range(nqubits - 1)), nqubits - 1)  # Multi-controlled Toffoli
    circuit.h(nqubits - 1)
    # Finish diffusion operator
    circuit.x(range(nqubits))
    circuit.h(range(nqubits))
    return circuit


class SATDialog(QDialog):
    def __init__(self, parent=None):
        super(SATDialog, self).__init__(parent)
        self.setWindowTitle("Enter SAT Instance")
        layout = QVBoxLayout()
        self.lineEdit = QLineEdit(self)
        self.okButton = QPushButton("OK", self)
        self.okButton.clicked.connect(self.accept)
        layout.addWidget(self.lineEdit)
        layout.addWidget(self.okButton)
        self.setLayout(layout)

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

    def plot(self):
        self.axes.plot([0,1,2,3,4], [10,1,20,3,40])

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Grover\'s Algorithm Demo')
        self.showFullScreen()
        
        self.initUI()

    def initUI(self):
        widget = QWidget()
        self.setCentralWidget(widget)
        
        # Layout
        mainLayout = QVBoxLayout()
        topLayout = QHBoxLayout()
        plotLayout = QVBoxLayout()  # Sub-layout for the plots
        buttonLayout = QHBoxLayout()
        
        # Image
        imageLabel = QLabel(self)
        pixmap = QPixmap('Grover.png')
        imageLabel.setPixmap(pixmap.scaledToWidth(self.width() * 2 / 3))
        
        # Plots
        plot1 = PlotCanvas(self, width=5, height=4)
        plot1.plot()
        plot2 = PlotCanvas(self, width=5, height=4)
        plot2.plot()

        # Buttons
        diffuseButton = QPushButton("Diffuse")
        oracleButton = QPushButton("Oracle")
        oracleFunctionButton = QPushButton("F(x)")
        oracleFunctionButton.clicked.connect(self.showSATDialog)

        resetButton = QPushButton("Reset")
        resetButton.clicked.connect(self.resetCircuit)
        
        self.nqubits = 4
        self.circuit = QuantumCircuit(self.nqubits, self.nqubits)
        self.circuit.h(range(self.nqubits))  # Apply Hadamard to all qubits
        
        # Bind buttons
        diffuseButton.clicked.connect(self.on_diffuse_clicked)
        oracleButton.clicked.connect(self.on_oracle_clicked)

        # Adjust button size
        buttons = [diffuseButton, oracleButton, oracleFunctionButton, resetButton]
        for button in buttons:
            button.setFixedSize(100, 30)  # Example fixed size, adjust as needed
            buttonLayout.addWidget(button)

        # Adding to layout
        topLayout.addWidget(imageLabel, 2)
        self.plot1 = plot1
        self.plot2 = plot2
        plotLayout.addWidget(plot1)
        plotLayout.addWidget(plot2)
        topLayout.addLayout(plotLayout, 1)
        
        mainLayout.addLayout(topLayout, 3)
        mainLayout.addLayout(buttonLayout, 1)
        
        widget.setLayout(mainLayout)
        self.oracle_count = 0
        self.diffusion_count = 0
        self.marked_states = ["0111", "1011"]

    def resetCircuit(self):
        self.nqubits = 4
        self.circuit = QuantumCircuit(self.nqubits, self.nqubits)
        self.circuit.h(range(self.nqubits))  # Apply Hadamard to all qubits
        self.oracle_count = 0
        self.diffusion_count = 0

    def on_oracle_clicked(self):
        oracle = grover_oracle(self.marked_states)
        temp = self.circuit
        self.oracle_count += 1
        self.circuit = self.circuit.compose(oracle)
        self.update_plots()
        self.circuit = temp
    
    def on_diffuse_clicked(self):
        oracle = grover_oracle(self.marked_states)
        self.circuit = self.circuit.compose(GroverOperator(oracle))
        self.diffusion_count += 1
        self.update_plots()

    def showSATDialog(self):
        dialog = SATDialog(self)
        if dialog.exec_():
            self.marked_states = []
            for item in dialog.lineEdit.text().split(','):
                self.marked_states.append(str(item.replace(" ", "").replace(",", "")))
            print(self.marked_states)
            print(type(self.marked_states))

    def update_plots(self):
        # Simulate the circuit
        provider = BasicProvider()
        backend = provider.get_backend("basic_simulator")
        temp = self.circuit
        for qubit in range(self.nqubits):
        	temp.measure(qubit, qubit)
        temp = transpile(temp, backend)
        result = backend.run(temp, shots=2048).result()
        counts  = result.get_counts(temp)

        # Update the probability histogram
        self.plot1.axes.clear()
        self.plot1.axes.bar(counts.keys(), counts.values())
        self.plot1.draw()
        
        # Convert counts to probabilities
        shots = sum(counts.values())
        probabilities = {state: count / shots for state, count in counts.items()}

        # Calculate components for the 2D coordinate plane
        parallel_component = sum(probabilities[state] for state in probabilities if state in self.marked_states)
        orthogonal_component = sum(probabilities[state] for state in probabilities if state not in self.marked_states)

   	    # Clear the plot
        self.plot2.axes.clear()

        # Draw the coordinate plane
        self.plot2.axes.axhline(0, color='black')
        self.plot2.axes.axvline(0, color='black')

        # Plot the unit vector in the current 'direction' of the state
        # Normalize the components to make it a unit vector
        vector_length = np.sqrt(parallel_component**2 + orthogonal_component**2)
        norm_parallel = parallel_component / vector_length
        norm_orthogonal = orthogonal_component / vector_length
        self.plot2.axes.quiver(0, 0, norm_orthogonal, norm_parallel, 
                           angles='xy', scale_units='xy', scale=1)

    	# Set the limits and labels
        self.plot2.axes.set_xlim(-0.1, 1.1)
        self.plot2.axes.set_ylim(-0.1, 1.1)
        self.plot2.axes.set_xlabel('|f(x) = 0>')
        self.plot2.axes.set_ylabel('|f(x) = 1>')
        self.plot2.axes.set_aspect('equal')

    	# Draw the plot
        self.plot2.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
