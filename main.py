import time

# Importa los modulos
from common.loader import load_dimacs_col
# from assignment_1.backtracking import backtracking
from assignment_1.dsatur import dSatur_alt


def run_benchmark(func, instance, runs=20):
    """Mide el tiempo promedio de ejecución de un algoritmo."""
    start = time.perf_counter_ns()
    for _ in range(runs):
        result = func(instance)
    end = time.perf_counter_ns()
    
    avg_time_ms = ((end - start) / runs) / 1e6
    return result, avg_time_ms

def run_dimacs_benchmark(file_path: str, known_optimal_k: int):
    """Mide el tiempo promedio de ejecución de un algoritmo y el K resultante."""
    print(f"\n--- Analizando archivo: {file_path} (Optimo conocido K={known_optimal_k}) ---")
    
    # 1. Cargar el grafo DIMACS
    graph = load_dimacs_col(file_path)
    print(f"Vértices: {graph.num_vertices}, Aristas calculadas.")

    solvers = [
        ("DSatur", dSatur_alt),
        # ("Backtrackinng", backtracking),
    ]

    for name, solver_func in solvers:
        start_time = time.perf_counter_ns()
        color_mapping = solver_func(graph)
        elapsed_ms = (time.perf_counter_ns() - start_time) / 1e6

        # Calcular el K obtenido (máximo color usado + 1)
        achieved_k = max(color_mapping.values()) + 1 if color_mapping else 0
        
        print(f"[{name}] K obtenido: {achieved_k} | Tiempo: {elapsed_ms:.4f} ms")

if __name__ == "__main__":

    run_dimacs_benchmark("data/dsjc250.5.col", known_optimal_k=28)
    run_dimacs_benchmark("data/dsjc500.1.col", known_optimal_k=12)

    run_dimacs_benchmark("data/dsjc1000.1.col", known_optimal_k=20)
    run_dimacs_benchmark("data/dsjc1000.5.col", known_optimal_k=85)
    run_dimacs_benchmark("data/dsjc1000.9.col", known_optimal_k=223)

    run_dimacs_benchmark("data/le450_25c.col", known_optimal_k=25)
    run_dimacs_benchmark("data/le450_25d.col", known_optimal_k=25)
    