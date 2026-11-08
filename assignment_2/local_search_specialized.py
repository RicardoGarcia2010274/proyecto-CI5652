import math, random 

from assignment_1.dsatur import dSatur_alt
from assignment_1.local_search_ia import Coloracion, _arranque
from common.representation import Graph


def _compactar_colores(color: dict[int, int]) -> dict[int, int]:
    equivalentes = {
        color_original: nuevo
        for nuevo, color_original in enumerate(sorted(set(color.values())))
    }
    return {v: equivalentes[c] for v, c in color.items()}


def _tabu_fijo(
    sol: Coloracion,
    max_iter: int,
    tenure: int,
) -> tuple[dict[int, int], int]:
    mejor = sol.color.copy()
    f_mejor = sol.f
    tabu: dict[tuple[int, int], int] = {}

    for paso in range(1, max_iter + 1):
        if sol.f == 0:
            break

        delta_minimo = None
        candidatos = []

        for v in sol.g.adj_list:
            color_actual = sol.color[v]
            gamma = sol.gamma[v]
            conflictos_actuales = gamma[color_actual]

            for color_nuevo in range(sol.k):
                if color_nuevo == color_actual:
                    continue

                delta = gamma[color_nuevo] - conflictos_actuales
                movimiento_tabu = tabu.get((v, color_nuevo), 0) > paso
                cumple_aspiracion = sol.f + delta < f_mejor

                if movimiento_tabu and not cumple_aspiracion:
                    continue

                if delta_minimo is None or delta < delta_minimo:
                    delta_minimo = delta
                    candidatos = [(v, color_nuevo)]
                elif delta == delta_minimo:
                    candidatos.append((v, color_nuevo))

        if not candidatos:
            break

        v, color_nuevo = random.choice(candidatos)
        color_anterior = sol.color[v]
        sol.mover(v, color_nuevo, registrar=False)
        tabu[(v, color_anterior)] = paso + tenure

        if sol.f < f_mejor:
            mejor = sol.color.copy()
            f_mejor = sol.f

    return mejor, f_mejor


def tabu_search(
    grafo: Graph,
    max_iter: int = 10_000,
    tenure: int | None = None,
    semilla: int | None = None,
) -> dict[int, int]:
    if max_iter <= 0:
        raise ValueError("max_iter debe ser mayor que cero")
    if tenure is not None and tenure <= 0:
        raise ValueError("tenure debe ser mayor que cero")
    if semilla is not None:
        random.seed(semilla)

    mejor = _compactar_colores(dSatur_alt(grafo))
    k = len(set(mejor.values()))
    tenure = tenure if tenure is not None else max(5, len(grafo.adj_list) // 20)

    while k > 1:
        k -= 1
        sol = Coloracion(grafo, k, _arranque(grafo, mejor, k))
        candidato, conflictos = _tabu_fijo(sol, max_iter, tenure)

        if conflictos > 0:
            break

        mejor = candidato

    return mejor


def _recocido_fijo(
    sol: Coloracion,
    temperatura_inicial: float,
    temperatura_final: float,
    enfriamiento: float,
    pasos_por_temperatura: int,
) -> tuple[dict[int, int], int]:
    mejor = sol.color.copy()
    f_mejor = sol.f
    temperatura = temperatura_inicial
    vertices = tuple(sol.g.adj_list)

    while temperatura > temperatura_final and sol.f > 0:
        for _ in range(pasos_por_temperatura):
            if sol.f == 0:
                break

            v = random.choice(vertices)
            color_actual = sol.color[v]
            color_nuevo = random.randrange(sol.k - 1)
            if color_nuevo >= color_actual:
                color_nuevo += 1

            gamma = sol.gamma[v]
            delta = gamma[color_nuevo] - gamma[color_actual]

            if delta <= 0 or random.random() < math.exp(-delta / temperatura):
                sol.mover(v, color_nuevo, registrar=False)

                if sol.f < f_mejor:
                    mejor = sol.color.copy()
                    f_mejor = sol.f

        temperatura *= enfriamiento

    return mejor, f_mejor


def simulated_annealing(
    grafo: Graph,
    temperatura_inicial: float = 5.0,
    temperatura_final: float = 0.01,
    enfriamiento: float = 0.95,
    pasos_por_temperatura: int | None = None,
    semilla: int | None = None,
) -> dict[int, int]:
    if temperatura_final <= 0 or temperatura_inicial <= temperatura_final:
        raise ValueError("Se requiere temperatura_inicial > temperatura_final > 0")
    if not 0 < enfriamiento < 1:
        raise ValueError("enfriamiento debe estar entre 0 y 1")
    if pasos_por_temperatura is not None and pasos_por_temperatura <= 0:
        raise ValueError("pasos_por_temperatura debe ser mayor que cero")
    if semilla is not None:
        random.seed(semilla)

    mejor = _compactar_colores(dSatur_alt(grafo))
    k = len(set(mejor.values()))
    pasos = pasos_por_temperatura or max(1, len(grafo.adj_list))

    while k > 1:
        k -= 1
        sol = Coloracion(grafo, k, _arranque(grafo, mejor, k))
        candidato, conflictos = _recocido_fijo(
            sol,
            temperatura_inicial,
            temperatura_final,
            enfriamiento,
            pasos,
        )

        if conflictos > 0:
            break

        mejor = candidato

    return mejor


