__all__ = ["Graph"]

import random

from common.representation import Graph

from assignment_1.dsatur import dSatur

# Definición de tipos para mayor claridad
Individual = dict[int, int]

def count_conflicts(graph: Graph, coloring: dict[int, int]) -> int:
    """
    Cuenta cuántos nodos conectados tienen el mismo color.
    Complejidad: O(E) donde E es el número de aristas.
    """
    conflicts = 0
    for u, neighbors in graph.adj_list.items():
        color_u = coloring[u]
        for v in neighbors:
            if color_u == coloring[v]:
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
    """Genera una población inicial."""
    vertices = sorted(list(graph.adj_list.keys()))
    return [create_individual(vertices, k) for _ in range(population_size)]

def uniform_crossover(parent1: Individual, parent2: Individual, vertices: list[int]) -> Individual:
    """Cruce uniforme: cada color se hereda de uno de los padres con 50% de probabilidad."""
    child = {}
    for v in vertices:
        child[v] = parent1[v] if random.random() < 0.5 else parent2[v]
    return child

def mutate(individual: Individual, vertices: list[int], k: int, mutation_rate: float) -> Individual:
    mutated = individual.copy()
    for v in vertices:
        if random.random() < mutation_rate:
            mutated[v] = random.randint(0, k - 1)
    return mutated

# --- # 

def tournament_selection(scored_pop: list[tuple[float, int, Individual]], tournament_size: int = 3) -> Individual:
    """Selecciona el mejor individuo entre un subconjunto aleatorio (torneo)."""
    competitors = random.sample(scored_pop, tournament_size)
    competitors.sort(key=lambda x: x[0], reverse=True) # Ordenar por fitness descendente
    return competitors[0][2] # Retorna el genotipo del ganador

# def
# for generation in range(max_generations):
    #     Padres <- seleccionarPadres(Población)
    #     Hijos <- recombinar(Padres)
    #     Hijos <- mutar(Hijos)
    #     Población <- seleccionarSobreviviente(Población, Hijos)
    # retornar decodificar(mejor individuo en Población)


def genetic_algorithm_gcp(
    graph: Graph, k: int, 
    pop_size: int = 100, 
    max_generations: int = 500, 
    mutation_rate: float = 0.05
    ) -> tuple[Individual, int]:
    """
    Bucle principal del algoritmo genético para coloración de grafos.
    """
    vertices = sorted(list(graph.adj_list.keys()))
    population = initialize_population(graph, pop_size, k)
    
    best_overall_solution = None
    min_conflicts = float('inf')
    
    for generation in range(max_generations):
        # 1. Evaluar la población actual
        scored_pop = []
        for ind in population:
            conflicts = count_conflicts(graph, ind)
            fitness = 1.0 / (1.0 + conflicts)
            scored_pop.append((fitness, conflicts, ind))
            
            # Registrar el mejor resultado histórico
            if conflicts < min_conflicts:
                min_conflicts = conflicts
                best_overall_solution = ind.copy()
        
        # 2. Condición de parada por éxito (0 conflictos)
        if min_conflicts == 0:
            print(f"¡Solución válida encontrada en la generación {generation}!")
            break
            
        # Ordenar población por fitness descendente
        scored_pop.sort(key=lambda x: x[0], reverse=True)
        
        # 3. Elitismo: conservar al mejor individuo intacto para la siguiente generación
        new_population = [scored_pop[0][2]]
        
        # 4. Crear la nueva generación mediante operadores genéticos
        while len(new_population) < pop_size:
            parent1 = tournament_selection(scored_pop)
            parent2 = tournament_selection(scored_pop)
            
            child = uniform_crossover(parent1, parent2, vertices)
            child = mutate(child, vertices, k, mutation_rate)
            
            new_population.append(child)
            
        population = new_population
        
    return best_overall_solution, min_conflicts

def gen_gcp_binary_search(
    graph: Graph, 
    pop_size: int = 100, 
    max_gen: int = 500, 
    mutation_rate: float = 0.05
) -> dict[int, int] | None:
    """
    Encuentra el número cromático usando búsqueda binaria en el rango de k.
    """
    max_degree = max(len(neighbors) for neighbors in graph.adj_list.values()) if graph.adj_list else 0
    dsatur_colors = dSatur(graph)
    dsatur_k = max(dsatur_colors.values()) + 1 if dsatur_colors else len(graph.adj_list)
    low = 1
    high = min(dsatur_k, max_degree + 1)

    best_k = high
    best_coloring = dsatur_colors
    
    while low <= high:
        mid = (low + high) // 2
        print(f"\n[Búsqueda binaria en AG] Probando k = {mid} (Rango: [{low}, {high}])")
        
        # Si probamos un k menor al que ya sabemos que funciona, intentamos el AG
        solution, conflicts = genetic_algorithm_gcp(
            graph, mid, pop_size=pop_size, max_generations=max_gen, mutation_rate=mutation_rate
        )
        
        if conflicts == 0:
            best_k = mid
            best_coloring = solution
            high = mid - 1  # Intentamos buscar un número cromático aún menor
        else:
            low = mid + 1   # Con 'mid' colores no se pudo, necesitamos subir el límite inferior
            
    return best_coloring
