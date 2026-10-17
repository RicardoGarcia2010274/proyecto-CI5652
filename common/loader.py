from common.representation import Graph

def load_dimacs_col(filepath: str) -> Graph:
    """Carga un grafo  de un archivo DIMACS .col con formato estándar."""
    graph = Graph(num_vertices=0)
    edges_to_add = []

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Línea de comentario ignorable
            if line.startswith('c'):
                continue
            
            # Línea con info del problema: p edge num_vertices num_edges
            elif line.startswith('p'):
                parts = line.split()
                num_v = int(parts[2])
                graph = Graph(num_vertices=num_v)
            
            # Línea con info de artistas: e u v
            elif line.startswith('e'):
                parts = line.split()
                # DIMACS indexa desde el 1, convierte los IDs para empezar desde 0
                u = int(parts[1]) - 1
                v = int(parts[2]) - 1
                edges_to_add.append((u, v))

    # Añade las aristas parseadas al grafo
    for u, v in edges_to_add:
        graph.add_edge(u, v)

    return graph