"""
Traductor del componente de la ontología al sistema experto
"""

from typing import Any, Sequence
from rdflib import RDF, RDFS, Graph, Node, URIRef, Literal
from experta import Fact
from practica1.ontologia import ex
# from practica1.sistema_experto import Libro
from collections import defaultdict


def traducir(g: Graph) -> Sequence[Fact]:
    """
    Recibe un grafo de ontología y retorna una lista de hechos para el sistema experto.
    """

    # La variable `tripletas` es un diccionario cuyas llaves son sujetos del grafo de ontologías, y
    # sus valores son a su vez diccionarios que tienen de llave a los predicados y de valor un
    # `set` con los valores para dicho predicado asociados a dicho sujeto. Es decir, contiene toda
    # la información del grafo de ontología de una forma más fácilmente accesible.
    tripletas = defaultdict(lambda: defaultdict(set))

    # En este ciclo for se agregan los tripletas del grafo `g` a la variable `tripletas`.
    for subj, pred, obj in g:
        tripletas[subj][pred].add(obj)

    # `hechos` es la variable que va a ser retornada, con los hechos para el sistema experto
    hechos = []

    # En este ciclo for se realiza la traducción
    for subj, datos in tripletas.items():
        # traducción del tipo RDF.type a una clase de hecho:
        tipo = _traducir_tipo(datos[RDF.type])

        # si `tipo` es None, no es una instancia y no nos interesa agregarlo a la lista de hechos
        if tipo is None:
            continue

        # ya traducimos el tipo entonces lo eliminamos de los datos que quedan por traducir
        del datos[RDF.type]

        # traducimos los atributos que quedan por traducir
        atributos = _traducir_atributos(datos)

        # agregamos el hecho a la lista de hechos junto con sus atributos
        hechos.append(tipo(**atributos))

    return hechos


def _traducir_tipo(tipos: set[URIRef]) -> type[Fact] | None:
    """
    Recibe un `set` de tipos (objetos del predicado RDF.type) y retorna la clase de hecho
    correspondiente.

    Retorna None si el tipo es uno de los siguientes:
        - RDFS.Class
        - RDF.Property
        - RDFS.Resource
    """

    _eliminar_tipos_ignorados(tipos)

    if len(tipos) == 0:
        return None

    assert len(tipos) == 1, f"hay más de un tipo: {tipos}"

    match next(iter(tipos)):
        # case ex.Libro:
        #     return Libro
        case tipo:
            raise Exception(f"se intentó traducir un tipo desconocido: {tipo}")


def _eliminar_tipos_ignorados(tipos: set[URIRef]):
    """
    Elimina los siguientes tipos del `set` `tipos`:
        - RDFS.Class
        - RDF.Property
        - RDFS.Resource
    """

    tipos_ignorados = [RDFS.Class, RDFS.Resource, RDF.Property]
    for tipo in tipos_ignorados:
        if tipo in tipos:
            tipos.remove(tipo)


def _traducir_atributos(datos: dict[Node, set[Node]]) -> dict[str, Any]:
    """
    Recibe un diccionario de predicados con sus valores y retorna un diccionario de atributos con
    sus respectivos valores para ser usados en una clase de hecho del sistema experto
    """

    atributos = {}

    for pred, objs in datos.items():
        # se traduce el predicado a un nombre de atributo
        llave = _traducir_nombre_atributo(pred)

        for obj in objs:
            # se traduce el objeto a un valor que pueda ser usado en el sistema experto
            valor = _traducir_valor(obj)

            atributos[llave] = valor

            # FIXME: ver qué se hace en experta cuando un hecho tiene un atributo con varios valores?
            # por ahora, ignoramos los otros
            break

    return atributos


def _traducir_nombre_atributo(pred: Node) -> str:
    """
    Recibe un predicado de una tripleta en una ontología y retorna un nombre de atributo adecuado
    """

    match pred:
        case ex.titulo:
            return "title"
        case _:
            raise Exception(f"se encontró un predicado desconocido: {pred}")


def _traducir_valor(obj: Node) -> Any:
    """
    Recibe un objeto de una tripleta en una ontología y retorna el valor del objeto para ser usado
    como valor de un atributo de una clase de hecho del sistema experto
    """

    match obj:
        case Literal():
            return obj.value
        case _:
            raise Exception("se encontró un objeto desconocido")


# FIXME: probablemente al final sería mejor quitar los Exception e imprimir en su lugar
# advertencias, para que no se rompa el programa si llega a aparecer algo inesperado
