idS = {"H", "S", "T", "X", "Y", "Z", "X(1/2)", "Y(1/2)", "-", "M"}
idC = {"CNOT": 1, "CCX": 2, "CX": 1, "Toffoli": 2}
parsingFlag = False

class Gate:
    def __init__(self, name, target, controls=None):
        self.name = name
        self.target = target
        self.controls = controls if controls else []

    def __repr__(self):
        return f"{{'Name': '{self.name}', 'Controls': {self.controls}, 'Target': {self.target}}}"

def parse_circuit(grid):
    instructions = []
    num_rows = len(grid)
    num_cols = len(grid[0])

    for col in range(num_cols):
        controls = []
        target = None
        gate_type = None

        for row in range(num_rows):
            cell = grid[row][col]

            if cell == ' ':  # Ignore empty cells
                continue

            if cell == '*':  # Control qubit
                controls.append(row)

            elif cell in idC:  # Multi-qubit gate type
                if not gate_type:  # Only set gate type if not already set
                    gate_type = cell

            elif cell in idS:  # Process single-qubit gate
                if not gate_type:  # Ensure it's not a target of a multi-qubit gate
                    instructions.append(Gate(cell, row))

        # Process multi-qubit gate at the end of the column if present
        if gate_type:
            target_candidates = [row for row in range(num_rows) if grid[row][col] not in ('*', ' ') and row not in controls]
            if target_candidates:
                target = target_candidates[0]
                instructions.append(Gate(gate_type, target, controls))

    return instructions


def parse_instructions(num_rows, num_columns, instructions):
    new_grid = [[' ' for _ in range(num_columns)] for _ in range(num_rows)]

    for gate in instructions:
        gate_filled = False

        gate_name = gate.name
        gate_target = gate.target
        gate_controls = gate.controls

        controls_exist = len(gate_controls) > 0
        controls_min = min(gate_controls) if controls_exist else 0
        controls_max = max(gate_controls) if controls_exist else 0

        # Searching for the available column.
        for column in range(num_columns):
            # Generating occuption list, which indicates the availability of this gate on this column.
            occupation_list = []
            if controls_exist:
                occupation_list = [new_grid[control][column] != ' ' for control in range(controls_min, controls_max+1)]
            occupation_list.append(new_grid[gate_target][column] != ' ')

            if True in occupation_list:
                # Skipping this column if this column is not available.
                continue
            else:
                # Placing the gate since this column is available.
                if controls_exist:
                    for block in range(controls_min, controls_max+1):
                        new_grid[block][column] = '*' if block in gate_controls else '|'
                new_grid[gate_target][column] = gate_name

                gate_filled = True
                break
        
        # Throws an exception if a gate cannot be placed.
        if not gate_filled:
            raise RuntimeError("Gate filling process failed.")
    
    # Sanitizing the redundant information.
    for i in range(num_rows):
        for j in range(num_columns):
            if new_grid[i][j] == '|' or new_grid[i][j] == ' ':
                new_grid[i][j] = ''

    return new_grid