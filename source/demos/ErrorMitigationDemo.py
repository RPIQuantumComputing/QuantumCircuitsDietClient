import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeVigo
from qiskit.quantum_info import SparsePauliOp
import qiskit
from qiskit_ibm_runtime import QiskitRuntimeService, Estimator, Options, Sampler

# Build noise model from backend properties
backend = FakeVigo()
noise_model = NoiseModel.from_backend(backend)

# Get coupling map from backend
coupling_map = backend.configuration().coupling_map

# Get basis gates from noise model
basis_gates = noise_model.basis_gates

# Perform a noise simulation
backend = AerSimulator(noise_model=noise_model,
                       coupling_map=coupling_map,
                       basis_gates=basis_gates)

# No error mitigation
sampler_no_mitigation = qiskit.primitives.BackendSampler(backend, options={"resilience_level": 0, "shots": 5000})
# With error mitigation
sampler_with_mitigation = qiskit.primitives.BackendSampler(backend, options={"resilience_level": 1, "shots": 5000})

def run_circuit(backend, circuit, options=Options()):
    circuit.measure([0, 1, 2, 3, 4], [0, 1, 2, 3, 4])
    result = backend.run(circuit).result()
    return result.get_counts(0)

def error_mitigation_strategies(backend, circuit, resilience=0):
    average = 0
    H = SparsePauliOp("".join(list(["Z" for i in range(circuit.num_qubits)])))
    estimator = qiskit.primitives.BackendEstimator(backend, options={"resilience_level": resilience, "shots": 512})
    return estimator.run(circuit, H).result().values[0]

def add_noise(k):
    circ = QuantumCircuit(5, 5)
    for k in range(k):
        circ.h(0)
    return circ

def get_all_zeros(k):
    global backend
    global sampler_with_mitigation
    circ = QuantumCircuit(5, 5)
    for k in range(k):
        circ.x(0)
        circ.h(0)
        circ.x(0)
        circ.h(0)
        circ.cx(0,1)
    circ.measure(0, 0)
    result = sampler_with_mitigation.run(circ).result().quasi_dists[0][0]
    return result

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quantum Error Mitigation")
        self.setGeometry(300, 300, 1200, 800)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        self.error_dist_button = QPushButton("Error Distribution", self)
        self.error_dist_button.clicked.connect(self.plot_error_distribution)
        button_layout.addWidget(self.error_dist_button)

        self.mitigation_button = QPushButton("Mitigation Comparison", self)
        self.mitigation_button.clicked.connect(self.plot_mitigation_comparison)
        button_layout.addWidget(self.mitigation_button)

        self.strategies_button = QPushButton("Mitigation Strategies", self)
        self.strategies_button.clicked.connect(self.plot_mitigation_strategies)
        button_layout.addWidget(self.strategies_button)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

    def plot_error_distribution(self):
        plt.clf()
        plt.plot([i for i in range(1, 800, 100)], [get_all_zeros(i) for i in range(1, 800, 100)])
        plt.xlabel("Repetitions")
        plt.ylabel("Percent Change all 1s (In theory: 0%)")
        plt.savefig("error_distribution.png")
        pixmap = QPixmap("error_distribution.png")
        self.image_label.setPixmap(pixmap)

    def plot_mitigation_comparison(self):
        global sampler_no_mitigation
        global sampler_with_mitigation
        plt.clf()
        circ = QuantumCircuit(5, 5)
        circ.h(0)
        circ.h(1)
        circ.h(2)
        circ.h(3)
        circ.h(4)
        for i in range(5):
            for j in range(i+1, 5):
                circ.cx(i, j)
                circ.h(i)
                circ.h(j)
            circ.x(i)
            circ.y(i)
            circ.z(j)
        circ.measure(0,0)
        circ.measure(1,1)
        circ.measure(2,2)
        circ.measure(3,3)
        circ.measure(4,4)

        # No error mitigation
        result_no_mitigation = sampler_no_mitigation.run(circ).result().quasi_dists[0]

        # With error mitigation
        result_with_mitigation = sampler_with_mitigation.run(circ).result().quasi_dists[0]

        # Plotting the histograms
        fig, axs = plt.subplots(1, 2, figsize=(12, 5))

        # Plot without error mitigation
        axs[0].bar(result_no_mitigation.keys(), result_no_mitigation.values(), color='blue')
        axs[0].set_title('Without Error Mitigation')
        axs[0].set_xlabel('Outcome')
        axs[0].set_ylabel('Probability')

        # Plot with error mitigation
        axs[1].bar(result_with_mitigation.keys(), result_with_mitigation.values(), color='green')
        axs[1].set_title('With Error Mitigation')
        axs[1].set_xlabel('Outcome')
        axs[1].set_ylabel('Probability')

        plt.tight_layout()
        plt.savefig("mitigation_comparison.png")
        pixmap = QPixmap("mitigation_comparison.png")
        self.image_label.setPixmap(pixmap)

    def plot_mitigation_strategies(self):
        plt.clf()
        plt.bar(["Nothing", "TREX", "ZNE", "PEC"], [error_mitigation_strategies(backend, add_noise(30), i) for i in range(4)])
        plt.xlabel("Resilience Method")
        plt.ylabel("Estimation of all 1s State (Theory: 1.0)")
        plt.savefig("mitigation_strategies.png")
        pixmap = QPixmap("mitigation_strategies.png")
        self.image_label.setPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())