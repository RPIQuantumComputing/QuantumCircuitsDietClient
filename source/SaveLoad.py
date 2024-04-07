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

    if instStr != str(instructions):
        raise RuntimeError("Save file parsing failed.")
    
    parsedCircuit = ParseCircuit.parse_instructions(numRows, numColumns, instructions)
    
    return parsedCircuit


# The fatal and lame limit of a C programmer...
def parseInstStr(instStr):
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