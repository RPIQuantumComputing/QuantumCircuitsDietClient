import numpy as np
import sys
from qiskit.visualization import plot_bloch_vector
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import random  # Make sure to import random if you're using random.choices

current_bloch_vector = np.array([0, 1])  # Initialize as a 2D column vector for matrix multiplication

def bloch_vector_to_spherical(bloch_vector):
    """
    Convert a 2D Bloch vector to 3D spherical coordinates for Bloch sphere visualization.
    
    Args:
        bloch_vector (np.array): A 2D array representing the Bloch vector [a, b].
    
    Returns:
        np.array: A 1D array representing the 3D coordinates (x, y, z) on the Bloch sphere.
    """
    # Ensure the vector is normalized
    norm = np.linalg.norm(bloch_vector)
    # Normalized bloch vector
    a, b = bloch_vector / norm
    
    # Calculate angles assuming a and b are complex numbers for a generic qubit state
    # Theta (polar angle) is calculated from the magnitude of a
    theta = 2 * np.arccos(np.abs(a))
    
    # Phi (azimuthal angle) is calculated from the phase difference of b
    phi = np.angle(b)
    
    # Convert to Cartesian coordinates for Bloch sphere plotting
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    
    return np.array([x, y, z])

class BlochSphereVisualization(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Bloch Sphere Visualization')

        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        self.buttons = {
            'X': QPushButton('X'),
            'Y': QPushButton('Y'),
            'Z': QPushButton('Z'),
            'H': QPushButton('H'),
            'T': QPushButton('T'),
            'S': QPushButton('S'),
            'M': QPushButton('M'),
            'R0': QPushButton('Reset |0>'),
            'R1': QPushButton('Reset |1>'),
        }

        for label, button in self.buttons.items():
            button_layout.addWidget(button)
            button.clicked.connect(self.onButtonClick)

        # Matplotlib Figure
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        main_layout.addWidget(self.canvas)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        self.showMaximized()

    def onButtonClick(self):
        global current_bloch_vector
        sender = self.sender()
        self.figure.clear()
        
        # Reshape current_bloch_vector for matrix multiplication
        column_vector = np.reshape(current_bloch_vector, (2, 1))  # Reshape to a 2x1 column vector
        
        if sender.text() == 'X':
            column_vector = np.dot(np.array([[0, 1], [1, 0]]), column_vector)
        elif sender.text() == 'Y':
            column_vector = np.dot(np.array([[0, -1j], [1j, 0]]), column_vector)
        elif sender.text() == 'Z':
            column_vector = np.dot(np.array([[1, 0], [0, -1]]), column_vector)
       	if sender.text() == 'H':
       	    column_vector = np.dot(np.array([[1/np.sqrt(2), 1/np.sqrt(2)], [1/np.sqrt(2), -1/np.sqrt(2)]]), column_vector)
       	if sender.text() == 'S':
       	    column_vector =  np.dot(np.array([[1, 0], [0, 1.0j]]), column_vector)
       	if sender.text() == 'T':
       	    column_vector =  np.dot(np.array([[1, 0], [0, np.exp(1.0j * np.pi / 4)]]), column_vector)
        if sender.text() == 'Reset |0>':
            column_vector =  np.reshape(np.array([1,0]), (2,1))
        if sender.text() == 'Reset |1>':
            column_vector = np.reshape(np.array([0,1]), (2,1))
        if sender.text() == 'M':
            probability_0 = current_bloch_vector[0]**2
            probability_1 = current_bloch_vector[1]**2
            column_vector = np.reshape(random.choices([np.array([1,0]), np.array([0,1])], weights=(probability_0, probability_1), k=1)[0],  (2, 1))
        
        # Update current_bloch_vector with the result of the matrix operation
        current_bloch_vector = np.array([column_vector[0,0], column_vector[1,0]])  # Flatten back to 1D array for further processing
        
        # Convert the updated bloch vector to spherical coordinates and plot
        spherical_coords = bloch_vector_to_spherical(current_bloch_vector)
        print(spherical_coords)
        plot_bloch_vector(list(spherical_coords), ax=self.figure.add_subplot(111, projection='3d'))
        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BlochSphereVisualization()
    ex.show()
    sys.exit(app.exec_())