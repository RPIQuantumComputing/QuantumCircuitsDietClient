from datetime import datetime
import hashlib, json, os
import ParseCircuit


def saveCircuit(circuit):
    time = datetime.now()
    instructions = ParseCircuit.parse_circuit(circuit.grid)
    numRows = len(circuit.grid)
    numColumns = len(circuit.grid[0])

    # TO BE ADDED: RCSID + name + bool student
    hashData = str(time) + str(instructions) + str(numRows) + str(numColumns)
    hashObj = hashlib.sha256()
    hashObj.update(hashData.encode())
    hashHex = hashObj.hexdigest()

    saveData = {}
    saveData["hash"] = str(hashHex)
    saveData['time'] = str(time)
    saveData['row'] = numRows
    saveData['col'] = numColumns
    saveData["inst"] = str(instructions)

    dirName = "saves"
    fileName = "save.qc"
    jsonObj = json.dumps(saveData, indent=4)
    if not os.path.exists(dirName):
        os.makedirs(dirName)
    filePath = os.path.join(dirName, fileName)  
    with open(filePath, 'w') as saveFile:
        saveFile.write(jsonObj)
    
    print("Save successful.")


def loadCircuit():
    pass