from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit_ibm_runtime import Session, QiskitRuntimeService, Sampler, Options
from qiskit_aer import AerSimulator
import qiskit 

def filter_dictionary(data):
    # Create a new dictionary to store the filtered data
    filtered_data = {}
    
    # Iterate over each item in the original dictionary
    for key, value in data.items():
        # Split the key on the space
        parts = key.split()
        
        # Check if the key has exactly two parts and the second part is not all zeros
        if len(parts) == 2 and '00' in parts[1]:
            # If the condition is met, add it to the filtered dictionary
            filtered_data[parts[0]] = value
    
    return filtered_data

def injestRun(settings, operations):
    print("Recieved Request...")
    ## Assuming Qiskit for the moment.
    service = QiskitRuntimeService()
    options = Options()

    # Create Quantum Circuit
    num = settings['num_qubits']+1
    qc = QuantumCircuit(QuantumRegister(num), ClassicalRegister(num))

    # Add operations to the circuit
    for op in operations:
        op = eval(str(op))
        if op['Name'] == 'H':
            qc.h(op['Target'])
        elif op['Name'] == 'CNOT':
            qc.cx(op['Controls'][0], op['Target'])
        elif op['Name'] == 'Toffoli':
            qc.ccx(op['Controls'][0], op['Controls'][1], op['Target'])
        else:
            exec(f"qc.{op['Name'].lower()}({op['Target']})")

    qc.measure_all() 
    # Execute the circuit
    options.resilience_level = 3 if settings['errorMitigation'] == 'Intense' else 1 if settings['errorMitigation'] == 'Moderate' else 0 if settings['errorMitigation'] == 'Low' else 2
    options.optimization_level = 3 if settings['transpilation'] == 'Intense' else 2 if settings['transpilation'] == 'Moderate' else 1 if settings['transpilation'] == 'Low' else 0
    
    print("Running Circuit...")
    if('qasm' in settings['system']):
        print("Redirecting to local simulator...")
        aersim = AerSimulator()
        result = aersim.run(qc).result()
        print("Finished Circuit...")
        return filter_dictionary(result.get_counts(0))
    else:
        with Session(service=service, backend=settings['system']) as session:
            sampler = Sampler(session=session, options=options)
            if("qasm" not in settings['system']):
                job = sampler.run(circuits=qc, shots=int(settings['shots']))
            else:
                job = sampler.run(circuits=qc)
            result = job.result()
    
    print("Finished Circuit...")
    return result.quasi_dists[0]