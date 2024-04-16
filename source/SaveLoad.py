from datetime import datetime
import hashlib, json, os
import ParseCircuit


def saveCircuit(circuit):
    time = str(datetime.now())
    instructions = str(ParseCircuit.parse_circuit(circuit.grid))
    numRows = len(circuit.grid)
    numColumns = len(circuit.grid[0])

    # TO BE ADDED: RCSID + name + bool student
    hashData = time + instructions + str(numRows) + str(numColumns)
    hashObj = hashlib.sha256()
    hashObj.update(hashData.encode())
    hashHex = str(hashObj.hexdigest())

    saveData = {}
    saveData["hash"] = hashHex
    saveData['time'] = time
    saveData['row'] = numRows
    saveData['col'] = numColumns
    saveData["inst"] = instructions

    dirName = "saves"
    if not os.path.exists(dirName):
        os.makedirs(dirName)

    fileName = "save.qc"
    filePath = os.path.join(dirName, fileName) 

    jsonObj = json.dumps(saveData, indent=4)
    with open(filePath, 'w') as saveFile:
        saveFile.write(jsonObj)


def loadCircuit(mainGUI):
    dirName = "saves"
    filePath = os.path.join(dirName, "save.qc")
    if not (os.path.exists(dirName) or os.path.exists(filePath)):
        raise RuntimeError("Save file does not exist.")

    jsonString = ""
    with open(filePath, 'r') as loadFile:
        for line in loadFile:
            jsonString += line
    loadData = json.loads(jsonString)

    numRows = loadData['row']
    numColumns = loadData['col']
    instructionString = loadData['inst']

    instructions = parseInstructionString(instructionString)

    if instructionString != str(instructions):
        raise RuntimeError("Save file parsing failed.")
    
    parsedCircuit = ParseCircuit.parse_instructions(numRows, numColumns, instructions)
    placeGates(mainGUI, parsedCircuit)


def parseInstructionString(instStr):
    instStrLen = len(instStr)
    if instStrLen <= 2:
        return []

    gateStrList = []
    gateStrStart, gateStrEnd = 0, 0
    for i in range(instStrLen):
        if instStr[i] == '{':
            gateStrStart = i + 1
        elif instStr[i] == '}':
            gateStrEnd = i
        
        if gateStrStart != 0 and gateStrEnd != 0:
            gateStrList.append(instStr[gateStrStart:gateStrEnd])
            gateStrStart, gateStrEnd = 0, 0

    instructions = []
    for gateStr in gateStrList:
        gateInfo = gateStr.split(', ')
        gateNameStr = gateInfo[0]
        gateTargetStr = gateInfo[-1]

        gateNameStart = len("\'Name\': \'")
        gateNameEnd = len(gateNameStr) - 1
        gateName = gateNameStr[gateNameStart:gateNameEnd]

        gateControlsStart, gateControlsEnd = 0, 0
        for i in range(len(gateStr)):
            if gateStr[i] == '[':
                gateControlsStart = i + 1
            elif gateStr[i] == ']':
                gateControlsEnd = i
                break

        gateControlsStr = gateStr[gateControlsStart:gateControlsEnd]
        gateControls = []
        if gateControlsStr != '':
            gateControlsStrList = gateControlsStr.split(', ')
            gateControls = [int(i) for i in gateControlsStrList]

        gateTargetStart = len("\'Target\': ")
        gateTargetEnd = len(gateTargetStr)
        gateTarget = int(gateTargetStr[gateTargetStart:gateTargetEnd])

        instructions.append(ParseCircuit.Gate(gateName, gateTarget, gateControls))

    return instructions


def placeGates(mainGUI, parsedCircuit):
    num_rows = len(parsedCircuit)
    num_cols = len(parsedCircuit[0])

    for col in range(num_cols):
        single_qubit_gates = {}
        multi_qubit_gates = {}
        controls = []

        # Gathering information from the loadCircuit() column by column.
        for row in range(num_rows):
            if parsedCircuit[row][col] in mainGUI.singlequbit_gates.keys():
                if row in single_qubit_gates.keys():
                    raise RuntimeError("Multiple gates at the same place.")
                single_qubit_gates[row] = parsedCircuit[row][col]
            elif parsedCircuit[row][col] in mainGUI.multiqubit_gates.keys():
                if row in multi_qubit_gates.keys():
                    raise RuntimeError("Multiple gates at the same place.")
                multi_qubit_gates[row] = parsedCircuit[row][col]
            elif parsedCircuit[row][col] == '*':
                if row in controls:
                    raise RuntimeError("Multiple gates at the same place.")
                controls.append(row)

        if len(multi_qubit_gates) > 0:
            if len(multi_qubit_gates) != 1:
                raise RuntimeError("More than one multiqubit gates in a column.")
            elif len(controls) == 0:
                raise RuntimeError("Multiqubit gate with no control gates.")
            else:
                multi_qubit_gate_row, multi_qubit_gate_name = multi_qubit_gates.popitem()

                # Placing control gates.
                while len(controls) > 0:
                    control_row = controls.pop()
                    mainGUI.place_multiqubit_gate(multi_qubit_gate_name, col, control_row)

                # Placing multi-qubit gates.
                mainGUI.place_multiqubit_gate(multi_qubit_gate_name, col, multi_qubit_gate_row)

        # Placing single-qubit gates.
        while len(single_qubit_gates) > 0:
            single_qubit_gate_row, single_qubit_gate_name = single_qubit_gates.popitem()
            mainGUI.place_single_qubit_gate(single_qubit_gate_name, single_qubit_gate_row, col)
