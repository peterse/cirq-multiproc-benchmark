"""Simple benchmark suite for Cirq + multiproc."""
import time

import cirq
import numpy as np

import multiproc

SEED = 104010  # coins and dice.
CIRCUIT_DEPTH = 100
NUM_CIRCUITS_TO_RUN = 100
N_TRIALS = 10
OP_DENSITY = 0.99
N_QUBITS_MAX = 18

# Query true processor availability
if not multiproc.MultiprocContext().can_resize:
    raise ValueError("Cannot reschedule affinity on this OS. Terminating.")


# Define the function that will be benchmarked
# This is because the function passed to workers must be piclable.
def randcircuit_f(args):
    n, d, ops, seed = args
    cirq.Simulator().simulate(
        cirq.testing.random_circuit(n, d, ops, random_state=seed))
    return


# Collect benchmarking parameters
N_CPU = multiproc.available_cpus()
# Include a 'control' run at the end, which doesn't implement Pool at all
# and reflects the time it would take to just run NUM_CIRCUITS_TO_RUN in
# serial using automatic resource allocation.
cpu_iter = list(range(1, N_CPU + 1)) + [None]
print("Iterating CPU count over the following values:\n{}".format(cpu_iter))
qubit_iter = list(range(1, N_QUBITS_MAX))
print(
    "Iterating qubit count over the following values:\n{}".format(qubit_iter))
trials_iter = list(range(N_TRIALS))
print("Running random circuits for {} trials".format(N_TRIALS))

# Iterate over all benchmarking parameters
results = np.zeros((len(cpu_iter), len(qubit_iter), N_TRIALS),
                   dtype=np.float64)
for i, n_cpu in enumerate(cpu_iter):
    if n_cpu is not None:
        pool = multiproc.MultiprocContext(n_cpus=n_cpu).pool()
    for j, n_qubits in enumerate(qubit_iter):
        for k, trial in enumerate(trials_iter):

            # simulate NUM_CIRCUITS_TO_RUN-many circuits specified by the
            # parameter package below
            circuit_specs = [(n_qubits, CIRCUIT_DEPTH, OP_DENSITY, SEED + el)
                             for el in range(NUM_CIRCUITS_TO_RUN)]
            t0 = time.perf_counter()
            if n_cpu is not None:
                pool.map(randcircuit_f, circuit_specs)
            else:
                for package in circuit_specs:
                    randcircuit_f(package)
            results[i, j, k] = time.perf_counter() - t0
    pool.close()

fname = f"benchmark_{N_CPU}_{N_QUBITS_MAX}_{N_TRIALS}_{NUM_CIRCUITS_TO_RUN}"
np.save(fname, results)
print(f"Results saved to: {fname}.npy")
