import sys
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class Graph:
    """Representación de un grafo no dirigido usando lista de adyacencias"""
    num_vertices: int
    adj_list: dict[int, set[int]] = field(default_factory=dict)

    def add_edge(self, u, v):
        """Añade una arista no dirigida entre los vértices u y v."""
        self.adj_list.setdefault(u, set()).add(v)
        self.adj_list.setdefault(v, set()).add(u)

    def add_vertex(self, v):
        """Añade un vértice al grafo."""
        if v not in self.adj_list:
            self.adj_list[v] = set()
            self.num_vertices += 1
    
    def delete_vertex(self, v):
        """Elimina un vértice y todas sus aristas del grafo."""
        if v in self.adj_list:
            for neighbor in self.adj_list[v]:
                self.adj_list[neighbor].remove(v)
            del self.adj_list[v]
            self.num_vertices -= 1