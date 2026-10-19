"""
ILS mejorada para coloración de grafos (minimizar el número de colores).

Formulación: se fija k y se minimiza el número de aristas en conflicto.
  - Espacio de búsqueda: S_k = asignaciones {vértice: color} con colores en 0..k-1
    (pueden tener conflictos).
  - Función de evaluación: f(c) = nº de aristas con ambos extremos del mismo color.
    f(c) = 0  <=>  c es una coloración válida con k colores.
  - Vecindad: cambiar el color de UN vértice que esté en conflicto.
  - Cuando f = 0 se baja k en 1 y se repite.
"""
import random
import time
from assignment_1.dsatur import dSatur_alt
from common.representation import Graph


class Coloracion:
    """Solución con k colores (puede tener conflictos) y evaluación incremental."""

    def __init__(self, g: Graph, k: int, color: dict):
        self.g, self.k = g, k
        self.color = dict(color)
        # gamma[v][c] = nº de vecinos de v que tienen el color c
        self.gamma = {v: [0] * k for v in g.adj_list}
        for v, vecinos in g.adj_list.items():
            for w in vecinos:
                self.gamma[v][self.color[w]] += 1
        # vértices en conflicto y nº de aristas en conflicto (f)
        self.conf = {v for v in g.adj_list if self.gamma[v][self.color[v]] > 0}
        self.f = sum(self.gamma[v][self.color[v]] for v in g.adj_list) // 2
        self.diario = []                      # movimientos hechos, para poder deshacerlos

    def mover(self, v, c_nuevo, registrar=True):
        c_viejo = self.color[v]
        if c_viejo == c_nuevo:
            return
        gv = self.gamma[v]
        self.f += gv[c_nuevo] - gv[c_viejo]
        self.color[v] = c_nuevo
        if registrar:
            self.diario.append((v, c_viejo))
        if gv[c_nuevo] > 0:
            self.conf.add(v)
        else:
            self.conf.discard(v)
        for w in self.g.adj_list[v]:
            gw = self.gamma[w]
            gw[c_viejo] -= 1
            gw[c_nuevo] += 1
            cw = self.color[w]
            if cw == c_viejo and gw[c_viejo] == 0:
                self.conf.discard(w)
            elif cw == c_nuevo:
                self.conf.add(w)

    def deshacer(self):
        """Revierte todos los movimientos registrados (sin copiar la solución)."""
        while self.diario:
            v, c = self.diario.pop()
            self.mover(v, c, registrar=False)


# ---------------- Búsqueda local ----------------
def busqueda_local(sol: Coloracion, limite: float, max_planos: int = 50) -> Coloracion:
    """Descenso por mejor mejora sobre vértices en conflicto.
    Vecindad: cambiar el color de un vértice en conflicto.
    Nunca empeora f; permite movimientos de meseta (delta = 0) con lista tabú
    para no ciclar, y para cuando no hay mejora en `max_planos` pasos."""
    tabu = {}
    paso, planos, f_min = 0, 0, sol.f
    while sol.f > 0 and planos < max_planos and time.time() < limite:
        paso += 1
        mejor_delta, cand = None, []
        for v in sol.conf:
            ca, gv = sol.color[v], sol.gamma[v]
            base = gv[ca]
            for c in range(sol.k):
                if c == ca:
                    continue
                d = gv[c] - base
                if d > 0:
                    continue                                   # solo mejora o meseta
                if tabu.get((v, c), 0) > paso and sol.f + d >= f_min:
                    continue                                   # tabú (con aspiración)
                if mejor_delta is None or d < mejor_delta:
                    mejor_delta, cand = d, [(v, c)]
                elif d == mejor_delta:
                    cand.append((v, c))
        if not cand:
            break                                              # óptimo local
        v, c = random.choice(cand)
        a = sol.color[v]
        sol.mover(v, c)
        tabu[(v, a)] = paso + random.randint(0, 9) + int(0.6 * len(sol.conf))
        if sol.f < f_min:
            f_min, planos = sol.f, 0
        else:
            planos += 1
    return sol


# ---------------- Perturbación, memoria y aceptación ----------------
def perturbacion(sol: Coloracion, fuerza: int):
    """Recolorea al azar `fuerza` vértices en conflicto (donde está el problema)."""
    candidatos = list(sol.conf) or list(sol.g.adj_list)
    for v in random.sample(candidatos, min(fuerza, len(candidatos))):
        sol.mover(v, random.randrange(sol.k))


def crear_memoria(n: int, f_inicial: int, paciencia: int = 50) -> dict:
    base = max(2, n // 100)
    return {"fuerza_base": base, "fuerza": base, "fuerza_max": max(base, n // 10),
            "f_mejor": f_inicial, "sin_mejora": 0, "paciencia": paciencia}

def criterio_aceptacion(sol: Coloracion, f_antes: int, memoria: dict) -> bool:
    """True = se acepta la nueva solución; False = se deshace la iteración."""
    if sol.f < memoria["f_mejor"]:                       # nuevo récord
        memoria.update(f_mejor=sol.f, sin_mejora=0, fuerza=memoria["fuerza_base"])
        return True
    memoria["sin_mejora"] += 1
    estancado = memoria["sin_mejora"] % memoria["paciencia"] == 0
    if estancado:                                         # perturba más fuerte
        memoria["fuerza"] = min(memoria["fuerza"] + 1, memoria["fuerza_max"])
    return sol.f <= f_antes or estancado                  # mesetas siempre; empeorar solo si estancado


# ---------------- ILS completo ----------------
def _arranque(grafo: Graph, color: dict, k: int) -> dict:
    """Quita el color k: cada vértice de esa clase va al color con menos conflictos."""
    nuevo = {v: c for v, c in color.items() if c < k}
    for v in [v for v, c in color.items() if c >= k]:
        cuenta = [0] * k
        for w in grafo.adj_list[v]:
            if w in nuevo:
                cuenta[nuevo[w]] += 1
        minimo = min(cuenta)
        nuevo[v] = random.choice([c for c in range(k) if cuenta[c] == minimo])
    return nuevo

def ils_mejorada(grafo: Graph, limite_seg: float = 30.0, iter_por_k: int = 10**4,
                 paciencia: int = 50, semilla: int | None = None) -> dict:
    if semilla is not None:
        random.seed(semilla)
    limite = time.time() + limite_seg
    n = len(grafo.adj_list)

    inicial = dSatur_alt(grafo)                           # S0
    mapa = {c: i for i, c in enumerate(sorted(set(inicial.values())))}
    mejor = {v: mapa[c] for v, c in inicial.items()}      # colores 0..k-1 sin huecos
    k = len(mapa)

    while k > 1 and time.time() < limite:
        k -= 1                                            # intentamos con un color menos
        sol = Coloracion(grafo, k, _arranque(grafo, mejor, k))
        busqueda_local(sol, limite)                       # S* <- busquedaLocal(S0)
        memoria = crear_memoria(n, sol.f, paciencia)      # memoria
        for _ in range(iter_por_k):                       # criterio de terminación
            if sol.f == 0 or time.time() >= limite:
                break
            sol.diario.clear()
            f_antes = sol.f
            perturbacion(sol, memoria["fuerza"])          # S' <- perturbación(S*, memoria)
            busqueda_local(sol, limite)                   # S*' <- busquedaLocal(S')
            if not criterio_aceptacion(sol, f_antes, memoria):
                sol.deshacer()                            # S* se queda como estaba
        if sol.f > 0:
            break                                         # no se logró con k colores
        mejor = dict(sol.color)                           # solución válida con k colores
    return mejor


# ---------------- Función de evaluación (versión explícita) ----------------
def funcion_evaluacion(grafo: Graph, color: dict) -> int:
    """Nº de aristas en conflicto: ambos extremos con el mismo color. Se minimiza.
    Costo O(|E|). La clase Coloracion mantiene este mismo valor (f) de forma incremental."""
    return sum(1 for u, vecinos in grafo.adj_list.items()
               for v in vecinos if u < v and color[u] == color[v])

def es_valida(grafo: Graph, color: dict) -> bool:
    return funcion_evaluacion(grafo, color) == 0

def numero_colores(color: dict) -> int:
    return len(set(color.values()))