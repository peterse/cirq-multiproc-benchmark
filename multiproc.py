"""Management for distributed computing. Use at your own risk."""
import os
import multiprocessing


def available_cpus():
    """Query the number of available CPUs on the system.

    Default to one less than the total cpu count where this option exists.
    Otherwise, return '2' as a default number of processes to run in parallel.

    Returns:
        num_cpu (int): Number of cpus available for multiprocessing.
    """
    num_cpu = 2
    if hasattr(os, 'cpu_count') and os.cpu_count() is not None:
        num_cpu = os.cpu_count() - 2 if os.cpu_count() > 2 else os.cpu_count()
    return num_cpu


class MultiprocContext:
    """Context management for modifying cpu affinity."""
    def __init__(self, n_cpus=None):
        """Enter a context with modified cpu affinity, if allowed.

        This will attempt to override the affinity methods in the `os` module
        for spawning processes. If those methods are not supported in the
        caller's operating system, then this will fall back to `available_cpus`.
        """
        self.can_resize = hasattr(os, 'sched_getaffinity') and \
                hasattr(os, 'sched_setaffinity')
        if n_cpus is None:
            n_cpus = available_cpus()
        self.n_cpus = n_cpus
        self.procs = list(range(self.n_cpus))
        if self.can_resize:
            self.initial_affinity = os.sched_getaffinity(0)

    def __enter__(self):
        if self.can_resize:
            os.sched_setaffinity(0, self.procs)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if self.can_resize:
            os.sched_setaffinity(0, self.initial_affinity)

    def pool(self):
        """Return a multiprocessing Pool according to specified cpus.

        Returns:
            (multiprocessing.Pool): Pool object initialized using this context's
                available cpus.
        """
        return multiprocessing.Pool(processes=self.n_cpus)
