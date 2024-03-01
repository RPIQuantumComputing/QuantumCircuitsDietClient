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


def loadCircuit():
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
    instStr = loadData['inst']

    instructions = parseInstStr(instStr)
        
    return ParseCircuit.parse_instructions(numRows, numColumns, instructions)
