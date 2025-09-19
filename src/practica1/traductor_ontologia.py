"""
Traductor del componente de la ontología al sistema experto
"""

from typing import Any, Sequence
from rdflib import RDF, RDFS, XSD, BNode, Graph, Node, URIRef, Literal, DC
from rdflib.collection import Collection
from experta import Fact
from practica1.ontologia import RUTA, GEO
from practica1.sistema_experto import Evento, Nodo, Ruta, Semaforo, Via
from collections import defaultdict


# llave: predicado del grafo de ontologias asociado a un sujeto específico
# valor: valores de ese predicado asociados a un sujeto específico
Predicados = defaultdict[Node, set[Node]]

# llave: sujetos del grafo de ontologias
# valor: un diccionario donde
#   - llave: predicado del grafo de ontologias asociados al sujeto
#   - valor: valores de dicho predicado asociados al sujeto
Tripletas = defaultdict[Node, Predicados]


def traducir(g: Graph) -> Sequence[Fact]:
    """
    Recibe un grafo de ontología y retorna una lista de hechos para el sistema experto.
    """

    # La variable `tripletas` es un diccionario cuyas llaves son sujetos del grafo de ontologías, y
    # sus valores son a su vez diccionarios que tienen de llave a los predicados y de valor un
    # `set` con los valores para dicho predicado asociados a dicho sujeto. Es decir, contiene toda
    # la información del grafo de ontología de una forma más fácilmente accesible.
    tripletas: Tripletas = defaultdict(lambda: defaultdict(set))

    # En este ciclo for se agregan los tripletas del grafo `g` a la variable `tripletas`.
    for subj, pred, obj in g:
        tripletas[subj][pred].add(obj)

    # `hechos` es la variable que va a ser retornada, con los hechos para el sistema experto
    hechos = []

    # En este ciclo for se realiza la traducción
    for subj, datos in tripletas.items():
        # print()
        # print(f"Traduciendo sujeto {subj} con datos {datos}")
        # traducción del tipo RDF.type a una clase de hecho:
        tipo_clase, tipo_atributo = _traducir_tipo(datos[RDF.type])

        # si `tipo` es None, no es una instancia y no nos interesa agregarlo a la lista de hechos
        if tipo_clase is None:
            print(f"Advertencia: ignorando {subj}")  # TODO: eliminar esto
            print()
            print(f"\t{datos}")
            print()
            print()
            print()
            print()
            continue

        # ya traducimos el tipo entonces lo eliminamos de los datos que quedan por traducir
        del datos[RDF.type]

        # traducimos los atributos que quedan por traducir
        atributos = _traducir_atributos(tripletas, datos)

        hecho_traducido = tipo_clase(**atributos)

        if tipo_atributo is not None:
            hecho_traducido["tipo"] = tipo_atributo

        # agregamos el hecho a la lista de hechos junto con sus atributos
        hechos.append(hecho_traducido)

    return hechos


def _traducir_tipo(tipos: set[Node]) -> tuple[type[Fact] | None, str | None]:
    """
    Recibe un `set` de tipos (objetos del predicado RDF.type) y retorna la clase de hecho
    correspondiente, junto a un string tipo (valor del atributo tipo de esa clase de hecho), si
    es necesario (o None si no lo es).

    Retorna (None, None) si el tipo no se refiere a una instancia:
    """

    if not _es_instancia(tipos):
        return None, None

    _eliminar_tipos_ignorados(tipos)

    if len(tipos) == 0:
        return None, None

    assert len(tipos) == 1, f"hay más de un tipo: {tipos}"

    match next(iter(tipos)):
        case RUTA.Calle:
            return Via, "calle"
        case RUTA.Avenida:
            return Via, "avenida"
        case RUTA.Autopista:
            return Via, "autopista"
        case RUTA.Transversal:
            return Via, "transversal"
        case RUTA.Interseccion:
            return Nodo, "intersección"
        case RUTA.PuntoReferencia:
            return Nodo, "Punto_de_referencia"
        case RUTA.Semaforo:
            return Semaforo, None
        case RUTA.Evento:
            return Evento, None
        case RUTA.Ruta:
            return Ruta, None
        case RUTA.Carrera:
            return Via, "carrera"
        case tipo:
            raise Exception(f"se intentó traducir un tipo desconocido: {tipo}")


def _es_instancia(tipos: set[Node]):
    """
    Retorna True si el sujeto asociado a los `tipos` es una instancia
    Las siguientes no se consideran instancias:
        - Definiciones de clases
        - Definiciones de propiedades
        - Definiciones de tipos de datos
        - Definiciones de listas
    """

    tipos_que_no_son_instancias = {
        RDFS.Class,
        RDF.Property,
        XSD.boolean,
        XSD.string,
        XSD.double,
        XSD.integer,
        RDF.List,
    }
    return len(tipos.intersection(tipos_que_no_son_instancias)) == 0


def _eliminar_tipos_ignorados(tipos: set[Node]):
    """
    Elimina los siguientes tipos del `set` `tipos`:
        - RDFS.Resource
        - Clases si ya hay una subclase más específica
    """

    # eliminar tipos en `tipos_ignorados`
    tipos_ignorados = [RDFS.Resource]
    for tipo in tipos_ignorados:
        if tipo in tipos:
            tipos.remove(tipo)

    # eliminar tipos en las llaves del diccionario `tipos_ignorados_si_ya_hay` si existe alguno de
    # los tipos en el valor del diccionario
    tipos_ignorados_si_ya_hay = {
        RUTA.Nodo: [RUTA.Interseccion, RUTA.PuntoReferencia],
        GEO.SpatialThing: [
            RUTA.Interseccion,
            RUTA.Carrera,
            RUTA.Autopista,
            RUTA.Transversal,
            RUTA.Calle,
            RUTA.Avenida,
            RUTA.PuntoReferencia,
        ],
        RUTA.Via: [
            RUTA.Carrera,
            RUTA.Autopista,
            RUTA.Calle,
            RUTA.Avenida,
            RUTA.Transversal,
        ],
    }
    for tipo, alternativas in tipos_ignorados_si_ya_hay.items():
        if tipo in tipos:
            for alternativa in alternativas:
                if alternativa in tipos:
                    tipos.remove(tipo)
                    break


def _traducir_atributos(
    tripletas: Tripletas, datos: dict[Node, set[Node]]
) -> dict[str, Any]:
    """
    Recibe un diccionario de predicados con sus valores y retorna un diccionario de atributos con
    sus respectivos valores para ser usados en una clase de hecho del sistema experto
    """

    atributos = {}

    for pred, objs in datos.items():
        # print(f"\tTraduciendo predicado {pred}")
        # se traduce el predicado a un nombre de atributo
        llave, valor = _traducir_atributo(tripletas, pred, objs)
        if llave is None:
            continue
        atributos[llave] = valor

    return atributos


def _traducir_atributo(
    tripletas: Tripletas, pred: Node, objs: set[Node]
) -> tuple[str | None, Any | None]:
    """
    Traduce un predicado con sus objetos de un grafo de ontologías a una tupla (atributo, valor)
    para ser usado en la creación de un hecho del sistema experto

    Parámetros:
        - pred: un predicado de una tripleta en una ontología
        - objs: una lista de objetos asociados a dicho predicado
    Retorna:
        Una tupla con los siguientes valores:
        - el nombre del atributo
        - el valor del atributo
        Puede retornar (None, None) si se debería ignorar este atributo
    """

    match pred:
        case RUTA.nombre:
            return "nombre", _literal(objs)
        case RUTA.tipo:
            return "tipo", _literal(objs)
        case RUTA.via:
            return "via", _uri_ref_nombre(tripletas, objs)
        case RUTA.afectaVia:
            return "afecta_via", _uri_ref_nombre(tripletas, objs)
        case RUTA.seRelacionaCon:
            # FIXME: confirmar esta traducción
            return "se_relaciona_con", _uri_ref_nombres(tripletas, objs)
        case RUTA.conectaCon:
            return "vias_conectadas", _uri_ref_nombres(tripletas, objs)
        case RUTA.tieneSemaforo:
            # FIXME confirmar
            # se ignora porque ya se agrega esta información con la propiedad estaEnVia
            # del semaforo
            return None, None
        case RUTA.tieneSemaforoObj:
            # FIXME confirmar
            # se ignora porque ya se agrega esta información con la propiedad estaEnVia
            # del semaforo
            return None, None
        case RUTA.esConectada:
            # FIXME confirmar
            # se ignora porque ya se agrega esta información con la propiedad conectaCon
            # de la intersección
            return None, None
        case RUTA.tiempoEspera:
            return "tiempo_espera", _literal(objs)
        case RUTA.intersectaCon:
            return "intersecta_con", _uri_ref_nombres(tripletas, objs)
        case RUTA.fluidez:
            return "fluidez", _literal(objs)
        case RUTA.velocidadPromedio:
            return "velocidad_promedio", _literal(objs)
        case RUTA.estaEnVia:
            return "via", _uri_ref_nombre(tripletas, objs)
        case RUTA.esBidireccional:
            return "es_bidireccional", _literal(objs)
        case DC.title:
            return "nombre", _literal(objs)
        case RUTA.tieneDistancia:
            return "distancia", _literal(objs)
        case RUTA.tieneVias:
            return "vias", _collection_nombres(tripletas, objs)
        case RUTA.tiempoEstimado:
            return "tiempo_estimado", _literal(objs)
        case RUTA.cierreTotal:
            return "cierre_total", _literal(objs)
        case RUTA.duracion:
            return "duracion", _literal(objs)
        case RUTA.tieneNombre:
            return "nombre", _literal(objs)
        case _:
            raise Exception(f"se encontró un predicado desconocido: {pred}")


def _literal(objs: set[Node]) -> Any:
    """
    Retorna el valor del primer elemento de `objs` verificando que en realidad solo hay un elemento
    y que dicho elemento es un Literal
    """
    assert len(objs) == 1, f"len(objs) != 1, objs={objs}"
    obj = next(iter(objs))
    assert isinstance(obj, Literal)
    return obj.value


def _uri_ref_nombre(tripletas: Tripletas, objs: set[Node]) -> str:
    """
    Retorna el nombre del primer elemento de `objs` verificando que en realidad solo hay un
    elemento y que dicho elemento es un URIRef que además tiene un predicado RUTA:nombre
    """
    assert len(objs) == 1
    obj = next(iter(objs))
    assert isinstance(obj, URIRef)
    nombre = tripletas[obj][URIRef(RUTA.nombre)]
    return _literal(nombre)


def _uri_ref_nombres(tripletas: Tripletas, objs: set[Node]) -> list[str]:
    """
    Retorna los nombres de los elementos de `objs` verificando que dichos elementos son URIRef o BNode que además tienen un predicado RUTA:nombre si son URIRef
    """
    nombres = []
    for obj in objs:
        if isinstance(obj, URIRef):
            nombre = tripletas[obj][URIRef(RUTA.nombre)]
            nombres.append(_literal(nombre))
        elif isinstance(obj, BNode):
            nombre = str(obj)
            nombres.append(nombre)
    return nombres


def _collection_nombres(tripletas: Tripletas, objs: set[Node]) -> list[str]:
    """
    Retorna una lista con los nombres de los elementos de `objs` verificando que `objs` contenga una única collección cuyos elementos tengan valores para el predicado RUTA:nombre
    """
    assert len(objs) == 1
    lista = next(iter(objs))
    assert isinstance(lista, BNode)

    # obtener los elementos de la colleción en una lista de python
    elementos = _recorrer_collection(tripletas, tripletas[lista])

    # obtener los RUTA:nombre de los elementos de la colleción
    elementos = list(map(lambda e: _literal(tripletas[e][RUTA.nombre]), elementos))

    return elementos


def _recorrer_collection(tripletas: Tripletas, collection: Predicados) -> list[URIRef]:
    """
    Recorre la collección `collection` retornando una lista de URIRef (los elementos de la collección)
    """
    resultado = []
    cur = collection
    while True:
        assert len(cur[RDF.first]) == 1, f"len(first) != 1, first: {cur[RDF.first]}"
        first = next(iter(cur[RDF.first]))

        assert isinstance(first, URIRef), f"first is not an URIRef, first: {first}"

        resultado.append(first)

        assert len(cur[RDF.rest]) == 1
        rest = next(iter(cur[RDF.rest]))

        if rest == RDF.nil:
            break
        cur = tripletas[rest]
    return resultado


# FIXME: probablemente al final sería mejor quitar los Exception e imprimir en su lugar
# advertencias, para que no se rompa el programa si llega a aparecer algo inesperado
