"""GRASP para minimizar el numero de colores de una coloracion de grafos."""

from collections import Counter
import random

from common.representation import Graph


def _construccion_voraz_aleatorizada(
    grafo: Graph,
    alpha: float,
    rng: random.Random,
) -> dict[int, int]:
    """Construye una coloracion valida eligiendo vertices y colores desde RCL."""
    color: dict[int, int] = {}
    tamanos: Counter[int] = Counter()
    sin_colorear = set(grafo.adj_list)
    n = len(sin_colorear)

    while sin_colorear:
        prioridades: dict[int, float] = {}
        for v in sin_colorear:
            saturacion = len({color[w] for w in grafo.adj_list[v] if w in color})
            prioridades[v] = saturacion + len(grafo.adj_list[v]) / (n + 1)

        maxima = max(prioridades.values())
        minima = min(prioridades.values())
        umbral = maxima - alpha * (maxima - minima)
        rcl_vertices = [v for v in sin_colorear if prioridades[v] >= umbral]
        v = rng.choice(rcl_vertices)

        colores_vecinos = {color[w] for w in grafo.adj_list[v] if w in color}
        colores_disponibles = [
            c for c in tamanos if c not in colores_vecinos
        ]
        if colores_disponibles:
            costos = {c: -tamanos[c] for c in colores_disponibles}
            minimo = min(costos.values())
            maximo = max(costos.values())
            umbral = minimo + alpha * (maximo - minimo)
            rcl_colores = [c for c in colores_disponibles if costos[c] <= umbral]
            elegido = rng.choice(rcl_colores)
        else:
            elegido = max(tamanos, default=-1) + 1

        color[v] = elegido
        tamanos[elegido] += 1
        sin_colorear.remove(v)

    return color


def _mejora_local(grafo: Graph, color: dict[int, int], rng: random.Random) -> dict[int, int]:
    """Mueve vertices a clases existentes sin crear conflictos."""
    mejorada = color.copy()
    tamanos: Counter[int] = Counter(mejorada.values())

    while True:
        mejor_delta = (0, 0)
        movimientos: list[tuple[int, int]] = []

        for v, color_actual in mejorada.items():
            prohibidos = {mejorada[w] for w in grafo.adj_list[v]}
            tam_actual = tamanos[color_actual]
            for color_nuevo, tam_nuevo in tamanos.items():
                if color_nuevo == color_actual or color_nuevo in prohibidos:
                    continue

                delta = (
                    -1 if tam_actual == 1 else 0,
                    -(2 * (tam_nuevo - tam_actual) + 2),
                )
                if delta < mejor_delta:
                    mejor_delta = delta
                    movimientos = [(v, color_nuevo)]
                elif delta == mejor_delta:
                    movimientos.append((v, color_nuevo))

        if not movimientos:
            return mejorada

        v, color_nuevo = rng.choice(movimientos)
        color_actual = mejorada[v]
        mejorada[v] = color_nuevo
        tamanos[color_actual] -= 1
        if tamanos[color_actual] == 0:
            del tamanos[color_actual]
        tamanos[color_nuevo] += 1


def funcion_evaluacion(color: dict[int, int]) -> tuple[int, int]:
    """Prioriza menos colores y, en empate, clases de color mas concentradas."""
    tamanos = Counter(color.values())
    return len(tamanos), -sum(tamano * tamano for tamano in tamanos.values())


def grasp(
    grafo: Graph,
    max_iter: int = 100,
    alpha: float = 0.2,
    semilla: int | None = None,
) -> dict[int, int]:
    """Ejecuta GRASP con construccion aleatorizada y mejora local."""
    if max_iter <= 0:
        raise ValueError("max_iter debe ser mayor que cero")
    if not 0 <= alpha <= 1:
        raise ValueError("alpha debe estar entre 0 y 1")

    rng = random.Random(semilla)
    mejor: dict[int, int] | None = None

    for _ in range(max_iter):
        candidato = _construccion_voraz_aleatorizada(grafo, alpha, rng)
        candidato = _mejora_local(grafo, candidato, rng)
        if mejor is None or funcion_evaluacion(candidato) < funcion_evaluacion(mejor):
            mejor = candidato

    return mejor if mejor is not None else {}
