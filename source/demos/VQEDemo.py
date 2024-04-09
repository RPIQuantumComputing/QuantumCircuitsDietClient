import numpy as np
from qiskit.quantum_info import SparsePauliOp
import qiskit
import random
import qiskit_algorithms
from scipy.optimize import minimize
from qiskit.circuit import QuantumCircuit, Parameter
from qiskit.primitives import Estimator, Sampler
from qiskit import QuantumCircuit
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.compiler import transpile
from qiskit_algorithms.gradients import ParamShiftEstimatorGradient
from qiskit.circuit import QuantumCircuit, Parameter
from qiskit.circuit.library import RealAmplitudes
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import ParameterVector, Parameter
from qiskit.circuit.library import RealAmplitudes
import qiskit
from qiskit.quantum_info import Pauli
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

estimator = qiskit.primitives.Estimator(options={"shots": None, "approximation": True})

class VQEThread(QThread):
    sig_done = pyqtSignal(float, float, float, float, float)
    sig_cost_update = pyqtSignal(int, float)  # New signal for cost updates

    def __init__(self, j2_j1, ansatz_type, optimizer_type):
        super().__init__()
        self.j2_j1 = j2_j1
        self.ansatz_type = ansatz_type
        self.optimizer_type = optimizer_type

    def run(self):
        dim = [4, 4]
        ansatz_ibm, x0, opt = run_vqe(construct_hamiltonian(1.0, self.j2_j1, [[1/2 for i in range(dim[0])] for j in range(dim[1])]), self.ansatz_type, self.optimizer_type, self)
        neel_ham = neel_order(dim)
        dimer_ham = dimer_order(dim)
        spin_ham = spin_order(dim)
        spin_corr_ham = spin_correlation(dim)
        result = estimator.run([ansatz_ibm for i in range(4)], [neel_ham, dimer_ham, spin_ham, spin_corr_ham], parameter_values=[x0 for i in range(4)]).result().values
        self.sig_done.emit(opt, result[0], result[1], result[2], result[3])

    def update_cost(self, iteration, cost):
        self.sig_cost_update.emit(iteration, cost)

def construct_hamiltonian(j1, j2, grid):
  def nearest_neighbor(grid, i, j):
    i, j = i % len(grid[0]), j % len(grid)
    look_at = [[1, 0], [-1, 0], [0, 1], [0, -1]]
    result = []
    for element in look_at:
      dx, dy = element
      result.append([(i + dx) % len(grid[0]), (j + dy) % len(grid)])
    return result

  def next_nearest_neighbor(grid, i, j):
    look_at = [[1, 1], [1, -1], [-1, 1], [-1, -1]]
    result = []
    for element in look_at:
      dx, dy = element
      result.append([(i + dx) % len(grid[0]), (j + dy) % len(grid)])
    return result

  def generate_dot_product(grid, term, idxA, idxB):
    operation_template = ['I' for element in range(len(grid[0]) * len(grid))]
    dot_product = SparsePauliOp(('I' * len(grid[0]) * len(grid)), coeffs=[0])
    for direction in ['X', 'Y', 'Z']:
      operation = operation_template
      operation[idxA], operation[idxB] = direction, direction
      dot_product += SparsePauliOp("".join(operation), coeffs=[term])
    return dot_product


  hamilonian = SparsePauliOp(('I' * len(grid[0]) * len(grid)), coeffs=[0])
  for i in range(len(grid[0])):
    for j in range(len(grid)):
      n_neighbors = nearest_neighbor(grid, i, j)
      nn_neighbors = next_nearest_neighbor(grid, i, j)

      for neighbor in n_neighbors:
        idxA = (j * len(grid)) + i
        idxB = (neighbor[1] * len(grid)) + neighbor[0]
        hamilonian += generate_dot_product(grid, j1, idxA, idxB)
      for neighbor in nn_neighbors:
        idxA = (j * len(grid)) + i
        idxB = (neighbor[1] * len(grid)) + neighbor[0]
        hamilonian += generate_dot_product(grid, j2, idxA, idxB)

  return hamilonian.simplify()

def neel_order(dim):
    L = dim[0] * dim[1]
    neel_op = SparsePauliOp(('I' * L), coeffs=[0])

    for i in range(L):
        x, y = i % dim[0], i // dim[0]
        sign = (-1) ** (x + y)
        label = ['I'] * L
        label[i] = 'Z'
        neel_op += SparsePauliOp(''.join(label), coeffs=[sign])

    neel_op = neel_op.simplify()
    neel_op /= L  # Normalize the Néel operator

    return (neel_op @ neel_op).simplify()

def dimer_order(dim):
    Lx, Ly = dim
    num_spins = Lx*Ly
    dimer_op = SparsePauliOp(('I' * num_spins), coeffs=[0])
    normalization = 0

    for x in range(0, Lx//2, 2):
        for y in range(Ly):
            i = y * Ly + x
            j = ((x + 1) % Lx) + y * Ly
            sign = (-1)**(x)
            label = ['I'] * num_spins
            label[i] = label[j] = 'X'
            dimer_op += sign * SparsePauliOp(''.join(label), coeffs=[sign])
            label[i] = label[j] = 'Y'
            dimer_op += sign * SparsePauliOp(''.join(label), coeffs=[sign])
            label[i] = label[j] = 'Z'
            dimer_op += sign * SparsePauliOp(''.join(label), coeffs=[sign])
            normalization += 1

    dimer_op.simplify()

    for x in range(0, Lx//2, 3):
        for y in range(Ly):
            i = y * Ly + x
            j = ((x + 2) % Lx) + y * Ly
            sign = (-1)**(x)
            label = ['I'] * num_spins
            label[i] = label[j] = 'X'
            dimer_op += sign * SparsePauliOp(''.join(label), coeffs=[sign])
            label[i] = label[j] = 'Y'
            dimer_op += sign * SparsePauliOp(''.join(label), coeffs=[sign])
            label[i] = label[j] = 'Z'
            dimer_op += sign * SparsePauliOp(''.join(label), coeffs=[sign])
            normalization += 1

    dimer_op.simplify()

    for y in range(0, Ly//2, 2):
        for x in range(Lx):
            i = y * Ly + x
            j = ((y + 1) % Ly)*Ly + x
            sign = (-1)**(y)
            label = ['I'] * num_spins
            label[i] = label[j] = 'X'
            dimer_op += sign * SparsePauliOp(''.join(label), coeffs=[sign])
            label[i] = label[j] = 'Y'
            dimer_op += sign * SparsePauliOp(''.join(label), coeffs=[sign])
            label[i] = label[j] = 'Z'
            dimer_op += sign * SparsePauliOp(''.join(label), coeffs=[sign])
            normalization += 1

    dimer_op.simplify()

    for y in range(0, Ly//2, 3):
        for x in range(Lx):
            i = y * Ly + x
            j = ((y + 2) % Ly)*Ly + x
            sign = (-1)**(y)
            label = ['I'] * num_spins
            label[i] = label[j] = 'X'
            dimer_op += sign * SparsePauliOp(''.join(label), coeffs=[sign])
            label[i] = label[j] = 'Y'
            dimer_op += sign * SparsePauliOp(''.join(label), coeffs=[sign])
            label[i] = label[j] = 'Z'
            dimer_op += sign * SparsePauliOp(''.join(label), coeffs=[sign])
            normalization += 1

    dimer_op.simplify()
    dimer_op /= normalization
    return (dimer_op @ dimer_op).simplify()

def spin_order(dim):
    L = dim[0] * dim[1]
    spin_corr = SparsePauliOp(('I' * L), coeffs=[0])

    for i in range(L):
        for j in range(i+1, L):
            x1, y1 = i % dim[0], i // dim[0]
            x2, y2 = j % dim[0], j // dim[0]

            if abs(x1 - x2) + abs(y1 - y2) == 1:  # Nearest neighbors
                label = ['I'] * L
                label[i] = 'Z'
                label[j] = 'Z'
                spin_corr += SparsePauliOp(''.join(label), coeffs=[1])

    spin_corr = spin_corr.simplify()
    spin_corr /= L  # Normalize the spin correlation operator

    return spin_corr

def spin_correlation(dim, max_distance=None):
    L = dim[0] * dim[1]
    spin_corr = SparsePauliOp(('I' * L), coeffs=[0])

    for i in range(L):
        for j in range(i+1, L):
            x1, y1 = i % dim[0], i // dim[0]
            x2, y2 = j % dim[0], j // dim[0]

            distance = abs(x1 - x2) + abs(y1 - y2)
            if max_distance is None or distance <= max_distance:
                label = ['I'] * L
                label[i] = 'Z'
                label[j] = 'Z'
                coeff = 1 / (distance ** 2)  # Weight coefficient by inverse square of distance
                spin_corr += SparsePauliOp(''.join(label), coeffs=[coeff])

    spin_corr = spin_corr.simplify()
    spin_corr /= L  # Normalize the spin correlation operator

    return spin_corr

itr = 0
total = 0
def cost_func(x0, ansatz, H, estimator, vqe_thread):
    global itr
    global pm
    x0_new = np.append(x0, [0 for i in range(ansatz.num_parameters - len(x0))])
    ansatz_copy = ansatz.assign_parameters(x0_new)
    energy = estimator.run(ansatz_copy, H).result().values[0]
    print(f"Evaluation: {itr}, Energy: {energy}")
    vqe_thread.update_cost(itr, energy)  # Emit the cost update signal
    itr += 1
    return energy


import random
import copy
import numpy as np
from scipy.optimize import dual_annealing
from qiskit.circuit.library import RealAmplitudes, EfficientSU2, TwoLocal, PauliTwoDesign
from qiskit_algorithms.optimizers import SPSA, COBYLA, AQGD, NFT, SLSQP, IMFIL, BOBYQA, UMDA

ansatz = None
itr = 0
averages = []
average_gradient = []
total_losses = []
total_averages = []
comparison_value = [10, 25, 50, 100, 150, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100]
sampled_grads = []
historic_gradients = {}
hamiltonian_temp = None
best_so_far = None
value_best = 1e100
num_total = 0

def store_intermediate_result(eval_count, parameters, mean, std):
    global num_total
    print("Loss: ", mean, " Step: ", num_total)
    num_total += 1

def run_vqe(ham, ansatz_user, optimizer_user, vqe_thread):
    global ansatz, average_gradient, averages, total_losses, total_averages, sampled_grads, estimator, historic_gradients, hamiltonian_temp, best_so_far, value_best
    hamiltonian_temp = ham
    hamiltonian = ham

    def minimize_func(new_parameters):
        global ansatz, hamiltonian_temp, estimator, best_so_far, value_best
        energy = (cost_func(new_parameters, ansatz, hamiltonian_temp, estimator, vqe_thread))
        if value_best >= energy:
            value_best = energy
            best_so_far = ansatz
        return energy.real

    if(ansatz_user == "TwoLocal"):
    	ansatz = TwoLocal(16, 'rx', 'cz', reps=3, entanglement='linear', parameter_prefix='k')
    elif(ansatz_user == "RealAmplitudes"):
    	ansatz = RealAmplitudes(16, reps=3, entanglement='linear', parameter_prefix='k')
    else:
    	ansatz = EfficientSU2(16, reps=3, entanglement='linear', parameter_prefix='k')
    best_result = None
    best_parameters = None
    best_energy = float('inf')

    bounds = [(0, 2 * np.pi)] * ansatz.num_parameters
    if(optimizer_user == "SPSA"):
    	optimizer = SPSA(maxiter=100)
    elif(optimizer_user == "COBYLA"):
    	optimizer = COBYLA(maxiter=200)
    else:
    	optimizer = NFT(maxiter=200)
    x0 = np.random.random(ansatz.num_parameters) * np.pi * 2
    res = optimizer.minimize(minimize_func, x0, bounds=bounds)
    print("Results: ", res.fun)

    return ansatz, res.x, res.fun

def cost_func(x0, ansatz, H, estimator, vqe_thread):
    global itr
    global pm
    x0_new = np.append(x0, [0 for i in range(ansatz.num_parameters - len(x0))])
    ansatz_copy = ansatz.assign_parameters(x0_new)
    energy = estimator.run(ansatz_copy, H).result().values[0]
    print(f"Evaluation: {itr}, Energy: {energy}")
    vqe_thread.update_cost(itr, energy)  # Emit the cost update signal
    itr += 1
    return energy

class VQEApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.iterations = []
        self.costs = []

    def initUI(self):
        layout = QVBoxLayout()

        label_j2_j1 = QLabel('J2/J1 Ratio:')
        self.input_j2_j1 = QLineEdit()
        layout.addWidget(label_j2_j1)
        layout.addWidget(self.input_j2_j1)

        label_ansatz = QLabel('Ansatz:')
        self.combo_ansatz = QComboBox()
        self.combo_ansatz.addItems(['TwoLocal', 'RealAmplitudes', 'EfficientSU2'])
        layout.addWidget(label_ansatz)
        layout.addWidget(self.combo_ansatz)

        label_optimizer = QLabel('Optimizer:')
        self.combo_optimizer = QComboBox()
        self.combo_optimizer.addItems(['SPSA', 'NFT', 'COBYLA'])
        layout.addWidget(label_optimizer)
        layout.addWidget(self.combo_optimizer)

        self.button_run = QPushButton('Run VQE')
        self.button_run.clicked.connect(self.runVQE)
        layout.addWidget(self.button_run)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        # Matplotlib figure and canvas setup
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)

    def onCostUpdate(self, iteration, cost):
        self.iterations.append(iteration)
        self.costs.append(cost)
        self.updatePlot()

    def updatePlot(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(self.iterations, self.costs, 'b-')
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Cost')
        ax.set_title('Cost vs Iteration')
        self.canvas.draw()

    def runVQE(self):
        j2_j1 = float(self.input_j2_j1.text())
        ansatz_type = self.combo_ansatz.currentText()
        optimizer_type = self.combo_optimizer.currentText()

        self.thread = VQEThread(j2_j1, ansatz_type, optimizer_type)
        self.thread.sig_cost_update.connect(self.onCostUpdate)
        self.thread.sig_done.connect(self.onVQEDone)
        self.thread.start()

    def onVQEDone(self, opt, neel_corr, dimer_corr, local_z_corr, global_z_corr):
        self.result_text.append(f"Energy Evaluation: {opt}\nNeel Correlation: {neel_corr}\nDimer Correlation: {dimer_corr}\nLocal Z Correlation: {local_z_corr}\nGlobal Z Correlation: {global_z_corr}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VQEApp()
    ex.show()
    sys.exit(app.exec_())