__all__ = ["Graph"]

import random

# Definición de tipos para mayor claridad
Individual = dict[int, int]

def count_conflicts(graph: Graph, coloring: dict[int, int]) -> int:
    """
    Cuenta cuántos nodos conectados tienen el mismo color.
    Complejidad: O(E) donde E es el número de aristas.
    """
    conflicts = 0
    for u, neighbors in graph.adj_list.items():
        color_u = coloring(u)
        for v in neighbors:
            if color_u == coloring(v):
                conflicts += 1

    # Hay que tomar en cuenta que la arista se toma en cuenta dos veces
    # Una en u -> v y otra en v -> u
    return conflicts // 2

def calculate_fitness(graph: Graph, coloring: dict[int, int]) -> float:
    """
    Calcula la aptitud del individuo. 
    Retorna 1.0 si es una coloración válida sin conflictos.
    """
    conflicts = count_conflicts(graph, coloring)
    return 1.0 / (1.0 + conflicts)

def create_individual(vertices: list[int], k: int) -> Individual:
    """Crea un individuo asignando aleatoriamente un color de 0 a k-1 a cada vértice."""
    return {v: random.randint(0, k - 1) for v in vertices}

def initialize_population(graph: Graph, population_size: int, k: int) -> list[Individual]:
    """Genera una población inicial de tamaño `population_size`."""
    vertices = sorted(list(graph.adj_list.keys()))
    return [create_individual(vertices, k) for _ in range(population_size)]