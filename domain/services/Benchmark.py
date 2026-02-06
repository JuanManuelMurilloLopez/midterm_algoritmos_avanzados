import time
import tracemalloc


class Benchmark:
    def __init__(self, script_name, experiment_name, samples=None):
        """
        Title:
            Benchmark execution time and memory usage.

        Params:
            script_name (str): Nombre del script que ejecuta el experimento.
            experiment_name (str): Nombre corto del experimento.
            samples (int | None): Número de muestras procesadas.
        """
        self.script_name = script_name
        self.experiment_name = experiment_name
        self.samples = samples

        self.start_time = None
        self.end_time = None
        self.current_mem = None
        self.peak_mem = None

    def start(self):
        """
        Title:
            Start benchmark measurement.
        """
        tracemalloc.start()
        self.start_time = time.perf_counter()

    def stop(self):
        """
        Title:
            Stop benchmark measurement and collect results.
        """
        self.end_time = time.perf_counter()
        self.current_mem, self.peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    def result(self):
        """
        Title:
            Return benchmark results as dictionary.

        Returns:
            dict: Benchmark metrics.
        """
        return {
            "script": self.script_name,
            "experiment": self.experiment_name,
            "samples": self.samples,
            "time_sec": round(self.end_time - self.start_time, 6),
            "mem_current_mb": round(self.current_mem / 10**6, 3),
            "mem_peak_mb": round(self.peak_mem / 10**6, 3),
        }
