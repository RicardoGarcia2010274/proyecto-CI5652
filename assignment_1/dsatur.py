from common.representation import Graph

__all__ = ["Graph"]

def dSatur(graph: Graph):
    """Implementación propia de la heurística de DSatur para colorear un grafo."""
    # Empieza sin colores y con saturación 0 en todos los vértices
    colors = {}
    saturation = {v: 0 for v in graph.adj_list}
    uncolored_vertices = set(graph.adj_list.keys())

    max_saturation_vertex = -1
    max_saturation = 0

    # El primer vértice a elegir es aquel con el mayor grado
    for vertex in uncolored_vertices:
        neighbors = graph.adj_list[vertex]
        current_saturation = len(neighbors)
        if current_saturation > max_saturation:
            max_saturation_vertex = vertex
            max_saturation = current_saturation

    while len(uncolored_vertices) > 0:
        current_color = 0
        while max_saturation_vertex in uncolored_vertices:
            is_color_used = False
            for neighbor in graph.adj_list[max_saturation_vertex]:
                if colors.get(neighbor, -1) == current_color:
                    current_color += 1
                    is_color_used = True
            # Asignamos el color que no ha sido usado en los vecinos
            if not is_color_used:
                colors[max_saturation_vertex] = current_color
                uncolored_vertices.remove(max_saturation_vertex)
        max_saturation = 0

        # Aquí elegimos el próximo vértice a colorear
        for vertex in uncolored_vertices:
            neighbors = graph.adj_list[vertex]
            current_saturation = 0
            current_colors = set()
            for v in neighbors:
                if not (colors.get(v, -1) in current_colors):
                    current_saturation += 1
                    current_colors.add(colors.get(v, -1))

            if current_saturation > max_saturation:
                max_saturation_vertex = vertex
                max_saturation = current_saturation

    return colors

def dSatur_alt(graph: Graph):
    """Implementación de la IA de la heurística de DSatur."""
    # Inicialización de los colores y saturación
    colors = {}
    saturation = {v: 0 for v in graph.adj_list}
    uncolored_vertices = set(graph.adj_list.keys())

    while uncolored_vertices:
        # Selección del vértice con mayor saturación
        max_saturation_vertex = max(uncolored_vertices, key=lambda v: (saturation[v], len(graph.adj_list[v])))
        
        # Determinar el color más bajo disponible
        neighbor_colors = {colors.get(neighbor) for neighbor in graph.adj_list[max_saturation_vertex] if neighbor in colors}
        color = 0
        while color in neighbor_colors:
            color += 1
        
        # Asignar el color al vértice seleccionado
        colors[max_saturation_vertex] = color
        uncolored_vertices.remove(max_saturation_vertex)

        # Actualizar la saturación de los vecinos no coloreados
        for neighbor in graph.adj_list[max_saturation_vertex]:
            if neighbor in uncolored_vertices:
                saturation[neighbor] += 1

    return colors