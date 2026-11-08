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

def _arranque_diverso(grafo: Graph, color: dict[int, int], k: int) -> dict[int, int]:
    inicio = _arranque(grafo, color, k)
    vertices = list(inicio)
    cantidad = max(1, int(0.15 * len(vertices))) if vertices else 0

    for v in random.sample(vertices, cantidad):
        conteos = [0] * k
        for w in grafo.adj_list[v]:
            conteos[inicio[w]] += 1

        if random.random() < 0.25:
            inicio[v] = random.randrange(k)
        else:
            minimo = min(conteos)
            mejores_colores = [c for c in range(k) if conteos[c] == minimo]
            inicio[v] = random.choice(mejores_colores)

    return inicio


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

        for v in tuple(sol.conf):
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
        tenure_min = max(1, tenure // 2)
        tenure_max = max(tenure_min, (3 * tenure) // 2)
        tabu[(v, color_anterior)] = paso + random.randint(tenure_min, tenure_max)

        if sol.f < f_mejor:
            mejor = sol.color.copy()
            f_mejor = sol.f

    return mejor, f_mejor


def tabu_search_ia(
    grafo: Graph,
    max_iter: int = 3_000,
    tenure: int | None = None,
    semilla: int | None = None,
    reinicios_por_k: int = 3,
) -> dict[int, int]:
    if max_iter <= 0 or reinicios_por_k <= 0:
        raise ValueError("max_iter y reinicios_por_k deben ser mayores que cero")
    if tenure is not None and tenure <= 0:
        raise ValueError("tenure debe ser mayor que cero")
    if semilla is not None:
        random.seed(semilla)

    mejor = _compactar_colores(dSatur_alt(grafo))
    k = len(set(mejor.values()))
    tenure = tenure if tenure is not None else max(5, len(grafo.adj_list) // 20)

    while k > 1:
        k -= 1
        mejor_k = None
        conflictos_mejor = math.inf

        for intento in range(reinicios_por_k):
            inicio = (
                _arranque(grafo, mejor, k)
                if intento == 0
                else _arranque_diverso(grafo, mejor, k)
            )
            sol = Coloracion(grafo, k, inicio)
            candidato, conflictos = _tabu_fijo(sol, max_iter, tenure)

            if conflictos < conflictos_mejor:
                mejor_k = candidato
                conflictos_mejor = conflictos

            if conflictos == 0:
                break

        if mejor_k is None or conflictos_mejor != 0:
            break

        mejor = mejor_k


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

            if sol.conf and random.random() < 0.9:
                v = random.choice(tuple(sol.conf))
            else:
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


def simulated_annealing_ia(
    grafo: Graph,
    temperatura_inicial: float = 5.0,
    temperatura_final: float = 0.01,
    enfriamiento: float = 0.95,
    pasos_por_temperatura: int | None = None,
    semilla: int | None = None,
    reinicios_por_k: int = 2,
) -> dict[int, int]:
    if temperatura_final <= 0 or temperatura_inicial <= temperatura_final:
        raise ValueError("Se requiere temperatura_inicial > temperatura_final > 0")
    if not 0 < enfriamiento < 1:
        raise ValueError("enfriamiento debe estar entre 0 y 1")
    if pasos_por_temperatura is not None and pasos_por_temperatura <= 0:
        raise ValueError("pasos_por_temperatura debe ser mayor que cero")
    if reinicios_por_k <= 0:
        raise ValueError("reinicios_por_k debe ser mayor que cero")
    if semilla is not None:
        random.seed(semilla)

    mejor = _compactar_colores(dSatur_alt(grafo))
    k = len(set(mejor.values()))
    pasos = pasos_por_temperatura or max(1, len(grafo.adj_list))

    while k > 1:
        k -= 1
        mejor_k: dict[int, int] | None = None
        conflictos_mejor = math.inf

        for intento in range(reinicios_por_k):
            inicio = (
                _arranque(grafo, mejor, k)
                if intento == 0
                else _arranque_diverso(grafo, mejor, k)
            )
            sol = Coloracion(grafo, k, inicio)
            candidato, conflictos = _recocido_fijo(
                sol,
                temperatura_inicial,
                temperatura_final,
                enfriamiento,
                pasos,
            )

            if conflictos < conflictos_mejor:
                mejor_k = candidato
                conflictos_mejor = conflictos

            if conflictos == 0:
                break

        if mejor_k is None or conflictos_mejor != 0:
            break

        mejor = mejor_k

    return mejor


