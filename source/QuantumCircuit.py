from ParseCircuit import parse_circuit

class Circuit:
	def __init__(self, debug=True):
		self.debug = debug
		self.defined = False

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

	def run_circuit(self):		
		instructions = parse_circuit(self.grid)
		self.instructions = instructions

		if(self.debug):
			for instruction in instructions:
				print(instruction)