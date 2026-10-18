#Algoritmo de Busqueda Local 
#Se tomo como representacion del grafo una lista de adyacencias
#Definimos un espacio combinatorion y una funcion de evaluacion 
from assignment_1.dsatur import dSatur_alt
from common.representation import Graph
from assignment_1.utils.espacio import CombinatorialSpace
from collections import Counter
import random
import time 

#la funcion que vamos a minimizar es el numero de colores usados para pintar el grafo
def funcion_evaluacion(solucion: dict) -> tuple:
    """(nº de colores, -suma de cuadrados de los tamaños de clase). Se minimiza.
    El segundo término desempata: favorece clases desiguales, más fáciles de vaciar."""
    tamanos = Counter(solucion.values())
    return (len(tamanos), -sum(t * t for t in tamanos.values()))

def local_search(grafo: Graph, solucion: dict | None) -> dict:

    """
    Algoritmo de busqueda local que escoge una solucion como mejor 
    siempre que la solucion vista sea mejor que la solucion actual
    """



    #si no me dan una solucion inicial, la creamos con Dsatur, en caso de que me la den uso esa
    if solucion is None: 
        mejor_actual = dSatur_alt(CombinatorialSpace(grafo).grafo)
    else:
        mejor_actual = solucion
 
    # Aqui calculamos los vecinos del mejor actual
    vecinos = CombinatorialSpace(grafo).get_neighbors(mejor_actual)

    #De todos los vecinos, vemos si hay alguna solucion mejor
    for element in vecinos: 
        if funcion_evaluacion(element) < funcion_evaluacion(mejor_actual):
            mejor_actual = element
    
    #NOTE: el criterio para elegir si una solucion es mejor que otra es simplemente
    # ver si la solucion que proponemos usa menos colores que la solucion anterior y ya

    return mejor_actual

#aqui definimos una perturbacion
def perturbacion(grafo: Graph, S: dict, memoria: dict) -> dict:

    """
    Funcion que usamos para realizar las perturbaciones de la buqeuda local iterada
    """

    nueva = S.copy()
    colores = set(nueva.values())
    for v in random.sample(list(nueva), min(memoria["fuerza"], len(nueva))):
        prohibidos = {nueva[w] for w in grafo.adj_list[v]}
        permitidos = [c for c in colores if c != nueva[v] and c not in prohibidos]
        if permitidos:
            nueva[v] = random.choice(permitidos)
    return nueva

#aqui definimos mi criterio de aceptacion 
def criterio_aceptacion(S: dict, S2: dict, memoria: dict) -> dict:

    """
    Funcion donde definimos el criterio de aceptacion ya que luego
    de realizar una perturbacion debemos comprobar si esta solucion arrojada sigue siendo valida
    """

    if funcion_evaluacion(S2) < funcion_evaluacion(S):
        memoria["sin_mejora"] = 0
        memoria["fuerza"] = memoria["fuerza_base"]        # vuelve a perturbar poco
        return S2
    memoria["sin_mejora"] += 1
    if memoria["sin_mejora"] % memoria["paciencia"] == 0:  # estancado: perturba más fuerte
        memoria["fuerza"] += 1
    if funcion_evaluacion(S2) == funcion_evaluacion(S):
        return S2                                           # acepta mesetas
    return S                                                # rechaza empeoramientos


def crear_memoria(grafo: Graph, fuerza_base: int | None = None, paciencia: int = 10) -> dict:
    
    """
    Crea la memoria usada por la busqueda local iterada, que dado un grafo, 
    define la fuerza de la perturbacion, que va subiendo mientras la busqueda se va 
    quedando apresada, un contador de las iteraciones sin mejorar y un numero de iteraciones 
    maximo permitidos sin que haya una mejora
    
    """
    
    fuerza_base = fuerza_base or max(2, len(grafo.adj_list) // 20)
    return {
        "fuerza_base": fuerza_base,   # fuerza a la que se vuelve tras una mejora
        "fuerza": fuerza_base,        # fuerza actual (sube si hay estancamiento)
        "fuerza_max": max(fuerza_base, len(grafo.adj_list) // 4),
        "sin_mejora": 0,              # iteraciones consecutivas sin mejorar
        "paciencia": paciencia,       # cada cuántas iteraciones sin mejora se sube la fuerza
    }


def es_valida(g, S):
    """Al terminar el algoritmo, verifica que dicha solucion sea valida"""

    return all(S[u] != S[v] for u in g.adj_list for v in g.adj_list[u])

def ils(grafo: Graph) -> dict: 

    """
    Algoritmo de la busqueda local iterada, que utiliza las funciones
    previamente descritas
    """
    actual = dict(dSatur_alt(grafo))
    tam = Counter(actual.values())                      # tamaño de cada clase de color

    while True:
        mejor, mejor_delta = None, (0, 0)
        for v, a in actual.items():
            prohibidos = {actual[w] for w in grafo.adj_list[v]}
            sa = tam[a]
            for b, sb in tam.items():
                if b == a or b in prohibidos:
                    continue
                # cambio en (nº de colores, -suma de cuadrados) al mover v de a a b
                delta = (-1 if sa == 1 else 0, -(2 * (sb - sa) + 2))
                if delta < mejor_delta:
                    mejor, mejor_delta = (v, a, b), delta
        if mejor is None:                               # óptimo local
            return actual
        v, a, b = mejor
        actual[v] = b
        tam[a] -= 1
        if tam[a] == 0:
            del tam[a]
        tam[b] += 1

#NOTE: Para samuel, estos son datos para probar, una vez veas que todo sirve 
# borra esta monda 
# random.seed(1)
# g = Graph(0)
# for v in range(40):
#     g.add_vertex(v)
# for u in range(40):
#     for v in range(u + 1, 40):
#         if random.random() < 0.3:
#             g.add_edge(u, v)

# inicial = dSatur_alt(g)
# final = ils(g)
# print("DSatur:", len(set(inicial.values())), "colores")
# print("ILS:   ", len(set(final.values())), "colores")
# print("Válida:", es_valida(g, final))