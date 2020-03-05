"""Plot results fron run.py"""
import argparse

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm

parser = argparse.ArgumentParser(description='Process benchmark results.')
parser.add_argument('target',
                    type=str,
                    metavar='t',
                    help='Benchmark target file')


def main(target):
    N_CPU, N_QUBITS_MAX, N_TRIALS, NUM_CIRCUITS_TO_RUN = [
        int(s) for s in target[:-4].split('_')[1:]
    ]
    cpu_iter = list(range(1, N_CPU + 1)) + [None]
    qubit_iter = list(range(1, N_QUBITS_MAX))
    trials_iter = list(range(N_TRIALS))
    results = np.load(target)

    # Color = processor count
    colors = cm.rainbow(np.linspace(0, 1, len(cpu_iter)))
    colors = [a.reshape(1, -1) for a in colors]

    # min_results = np.min(results, axis=2)
    fig, ax = plt.subplots()
    scatter_handles = []
    for i, (n_cpu, c) in enumerate(zip(cpu_iter, colors)):
        print(n_cpu)
        for j, n_qubits in enumerate(qubit_iter):
            for k in trials_iter:
                if n_cpu is None:
                    # Plot the baseline
                    ax.scatter(n_qubits,
                               np.min(results[i, j]),
                               c='k',
                               alpha=0.5,
                               label="",
                               marker="_",
                               s=400)
                else:
                    label = "" if (j or k) else f"{n_cpu}"
                    # plot the cpu-distributed results
                    ax.scatter([n_qubits] * N_TRIALS,
                               results[i, j, :],
                               c=c,
                               alpha=0.8,
                               label=label)

    leg = ax.legend(loc="upper left", title="CPU count")
    ax.add_artist(leg)

    ax.set_xlabel("Number of qubits")
    ax.set_xticks(qubit_iter)
    ax.set_ylabel("Time (s)")
    ax.set_ylim((0, ax.get_ylim()[1]))
    ax.set_title(
        f"Time to run a batch of {NUM_CIRCUITS_TO_RUN} circuits\n {N_TRIALS} trials of batches"
    )
    plt.show()


if __name__ == '__main__':
    args = parser.parse_args()
    main(**vars(args))
