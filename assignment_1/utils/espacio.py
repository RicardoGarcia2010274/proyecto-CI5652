#Espacio combinatorio usado en la busqueda local

class CombinatorialSpace:
    def __init__(self, grafo): 
        self.grafo = grafo

    def get_neighbors(self, coloring: dict) -> list[dict]:
        """Vecinos: cambiar el color de un vértice a otro color ya usado
        que no tenga ninguno de sus vecinos (así sigue siendo válida)."""
        neighbors = []
        colores = set(coloring.values())
        for v, c in coloring.items():
            prohibidos = {coloring[w] for w in self.grafo.adj_list[v]}
            for c_nuevo in colores:
                if c_nuevo != c and c_nuevo not in prohibidos:
                    nuevo = coloring.copy()
                    nuevo[v] = c_nuevo
                    neighbors.append(nuevo)
        return neighbors