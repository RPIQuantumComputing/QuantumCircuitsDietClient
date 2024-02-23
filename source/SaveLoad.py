from datetime import datetime
import hashlib, json
import ParseCircuit


def saveCircuit(circuit):
    instructions = ParseCircuit.parse_circuit(circuit.grid)
    time = datetime.now()

    hashData = str(time) + str(instructions) # TO BE ADDED: RCSID + name + bool student
    hashObj = hashlib.sha256()
    hashObj.update(hashData.encode())
    hashHex = hashObj.hexdigest()

    save = {}
    save["hash"] = str(hashHex)
    save['time'] = str(time)
    save["inst"] = str(instructions)

    jsonObj = json.dumps(save, indent=2)
    with open("save.json", 'w') as outfile:
        outfile.write(jsonObj)
    
    print("Save successful.")


def loadCircuit():
    pass