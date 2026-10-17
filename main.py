import time

# Importa los archivos
from assignment_1.backtracking import backtracking
from assignment_1.dsatur import dSatur

def run_benchmark(func, instance, runs=20):
    """Mide el tiempo promedio de ejecución de un algoritmo."""
    start = time.perf_counter_ns()
    for _ in range(runs):
        result = func(instance)
    end = time.perf_counter_ns()
    
    avg_time_ms = ((end - start) / runs) / 1e6
    return result, avg_time_ms