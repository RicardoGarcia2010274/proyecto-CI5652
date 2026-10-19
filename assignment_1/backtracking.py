import time
import sys
from pathlib import Path


from common.representation import Graph
from assignment_1.dsatur import dSatur  # Dsatur para un límite superior inicial


class SolverTimeoutError(Exception):
    """Raised when the exact solver exceeds the allocated timeout."""
    pass


def _can_color_with_k(graph: Graph, k: int, vertices: list[int], coloring: dict[int, int], index: int) -> bool:
    """Función de backtracking recursiva que verifica si un grafo se puede pintar con un máx de k colores."""

    # Caso base: vértices pintados satisfactoriamente
    if index == len(vertices):
        return True

    v = vertices[index]
    for color in range(k):
        # Check conflicts with neighbors
        conflict = any(coloring.get(nbr) == color for nbr in graph.adj_list[v])
        
        if not conflict:
            coloring[v] = color
            if _can_color_with_k(graph, k, vertices, coloring, index + 1):
                return True
            del coloring[v]

    return False


def backtracking(graph: Graph) -> dict[int, int]:
    """Encuentra el número cromático K de un grafo."""
    vertices = list(graph.adj_list.keys())
    
    # Se usa DSatur para tener un límite superior
    try:
        initial_dsatur = dSatur(graph)
        high = max(initial_dsatur.values()) + 1
    except Exception:
        high = graph.num_vertices

    low = 1
    best_coloring = initial_dsatur if 'initial_dsatur' in locals() else {}
    best_k = high

    while low <= high:
        mid = (low + high) // 2
        coloring = {}
        
        if _can_color_with_k(graph, mid, vertices, coloring, 0):
            best_k = mid
            best_coloring = coloring
            high = mid - 1  # Try to find a smaller K
        else:
            low = mid + 1   # Need more colors

    return best_coloring


# --- Local Standalone Test ---
if __name__ == "__main__":
    print("Probando Solver Exacto con Timeout...")
    g = Graph(num_vertices=4)
    # Form a 4-vertex cycle (Chromatic number should be 2 or 3 depending on edges, C4 needs 2)
    g.add_edge(0, 1)
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(3, 0)

    coloring, k = backtracking(g)
    print(f"K exacto encontrado: {k}")
    print(f"Asignación: {coloring}")