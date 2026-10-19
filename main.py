import time
import concurrent.futures
import multiprocessing

# Importa los modulos
from common.loader import load_dimacs_col
from assignment_1.backtracking import backtracking
from assignment_1.dsatur import dSatur_alt
from assignment_1.local_search import ils
from assignment_1.local_search_ia import ils_mejorada
from assignment_1.local_search import local_search

def run_benchmark(func, instance, runs=20):
    """Mide el tiempo promedio de ejecución de un algoritmo."""
    start = time.perf_counter_ns()
    for _ in range(runs):
        result = func(instance)
    end = time.perf_counter_ns()
    
    avg_time_ms = ((end - start) / runs) / 1e6
    return result, avg_time_ms

def _worker_target(solver_func, graph, queue):
    """Función auxiliar para ejecutar el solver en un proceso separado."""
    try:
        result = solver_func(graph)
        queue.put((result, None))
    except Exception as e:
        queue.put((None, e))

def _run_with_timeout(solver_func, graph, timeout_seconds):
    """Ejecuta un solver en un proceso separado y lo mata si excede el timeout."""
    queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=_worker_target, args=(solver_func, graph, queue))
    
    p.start()
    p.join(timeout=timeout_seconds)
    
    if p.is_alive():
        # Si sigue vivo tras el timeout, lo matamos de inmediato para que no se guise el programa
        p.terminate()
        p.join()
        return None, True  # TIMEOUT
        
    if queue.empty():
        return None, True
        
    result, error = queue.get()
    if error:
        raise error
        
    return result, False

def run_dimacs_benchmark(file_path: str, known_optimal_k: int, timeout_seconds: float = 100.0):
    """Mide el tiempo de ejecución de cada algoritmo, el K resultante y gestiona timeouts."""
    print(f"\n--- Analizando archivo: {file_path} (Óptimo conocido K={known_optimal_k}) ---")
    
    # Carga el grafo DIMACS
    graph = load_dimacs_col(file_path)
    print(f"Vértices: {graph.num_vertices}, Aristas calculadas.")

    solvers = [
        ("DSatur", dSatur_alt),
        #("Backtracking", backtracking),
        ("Búsqueda local", local_search),
        ("ils", ils),
        ("ils_ia", ils_mejorada)
    ]

    for name, solver_func in solvers:
        print(f"Ejecutando [{name}] (Límite: {timeout_seconds}s)...", end=" ", flush=True)
        
        start_time = time.perf_counter_ns()
        color_mapping, timed_out = _run_with_timeout(solver_func, graph, timeout_seconds)
        elapsed_ms = (time.perf_counter_ns() - start_time) / 1e6

        if timed_out:
            print(f"❌ TIMEOUT (Excedió {timeout_seconds}s)")
        else:
            # Calcular el K obtenido (máximo color usado + 1)
            achieved_k = max(color_mapping.values()) + 1 if color_mapping else 0
            print(f"✅ K obtenido: {achieved_k} | Tiempo: {elapsed_ms:.4f} ms")

if __name__ == "__main__":

    run_dimacs_benchmark("data/dsjc250.5.col", known_optimal_k=28)
    run_dimacs_benchmark("data/dsjc500.1.col", known_optimal_k=12)

    run_dimacs_benchmark("data/dsjc1000.1.col", known_optimal_k=20)
    run_dimacs_benchmark("data/dsjc1000.5.col", known_optimal_k=85)
    run_dimacs_benchmark("data/dsjc1000.9.col", known_optimal_k=223)

    run_dimacs_benchmark("data/le450_25c.col", known_optimal_k=25)
    run_dimacs_benchmark("data/le450_25d.col", known_optimal_k=25)

    run_dimacs_benchmark("data/flat300_28_0.col", known_optimal_k=28)
    run_dimacs_benchmark("data/flat1000_50_0.col", known_optimal_k=50)
    run_dimacs_benchmark("data/flat1000_76_0.col", known_optimal_k=76)

