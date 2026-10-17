from common.representation import Graph
from assignment_1.dsatur import dSatur

def create_sample_graph1() -> Graph:
    # 5 vértices
    g = Graph(num_vertices=5)
    
    # Anillo: 0-1-2-3-4-0
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
    for u, v in edges:
        g.add_edge(u, v)
        
    return g

def create_sample_graph2() -> Graph:
    # 5 vértices
    g = Graph(num_vertices=5)
    
    # La casita
    edges = [(0, 1), (0, 2), (1,2), (1,3), (1,4), (3,4), (2,4)]
    for u, v in edges:
        g.add_edge(u, v)
        
    return g


def main():
    print("=== Ejecutando Suite de Pruebas Principal ===")
    
    # 1. Generar un grafo de prueba
    graph = create_sample_graph2()
    print(f"Grafo generado con {graph.num_vertices} vértices.")

    # 2. Ejecutar DSatur
    solution = dSatur(graph)
    
    # 3. Mostrar resultados
    max_colors = max(solution.values()) + 1
    print(f"Colores totales utilizados: {max_colors}")
    print("Asignación:", solution)

# --- Root Entry Point ---
# This runs when you type: python main.py
if __name__ == "__main__":
    main()