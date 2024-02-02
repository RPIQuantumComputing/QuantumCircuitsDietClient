from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit_ibm_runtime import Session, QiskitRuntimeService, Sampler, Options

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
    options.resilience_level = 3 if settings['errorMitigation'] == 'Intense' else 2 if settings['errorMitigation'] == 'Moderate' else 1 if settings['errorMitigation'] == 'Low' else 0
    options.optimization_level = 3 if settings['transpilation'] == 'Intense' else 2 if settings['transpilation'] == 'Moderate' else 1 if settings['transpilation'] == 'Low' else 0
    
    print("Running Circuit...")
    with Session(service=service, backend=settings['system']) as session:
        sampler = Sampler(session=session, options=options)
        job = sampler.run(circuits=qc, shots=int(settings['shots']))
        result = job.result()

    print("Finished Circuit...")
    return result.quasi_dists[0]