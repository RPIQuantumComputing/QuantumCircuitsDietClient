from ParseCircuit import parse_circuit
from ServerInterface import injestRun
import matplotlib.pyplot as plt

class Circuit:
	def __init__(self, debug=True):
		self.debug = debug
		self.defined = False
		self.settings = None

	def update_grid(self, new_grid):
		self.defined = True
		self.width = len(new_grid[0])
		self.height = len(new_grid)
		self.grid = new_grid

		if(self.debug):
			print("-------------GRID CHANGE----------------")
			for k in self.grid:
				print(k)
			print("------------------------------------------")

	def run_circuit(self, settings=None):
		if(settings != None):
			self.settings = settings	
			self.settings['num_qubits'] = self.height	
		instructions = parse_circuit(self.grid)
		self.instructions = instructions
		results = injestRun(self.settings, self.instructions)

		try:
			return results
		except Exception as e:
			print(f"ERROR: Failed to run circuit! {e}")
			return dict()