"""
Traductor del componente de la ontología al sistema experto
"""

from typing import Any, Sequence
from rdflib import RDF, RDFS, XSD, BNode, Graph, Node, URIRef, Literal, DC
from experta import Fact
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
        # traducción del tipo RDF.type a una clase de hecho:
        tipo_clase, tipo_campo = _traducir_tipo(datos[RDF.type])

        # si `tipo` es None, no es una instancia y no nos interesa agregarlo a la lista de hechos
        if tipo_clase is None:
            continue

        # ya traducimos el tipo entonces lo eliminamos de los datos que quedan por traducir
        del datos[RDF.type]

        # traducimos los campos que quedan por traducir
        campos = _traducir_campos(tripletas, datos)

        hecho_traducido = tipo_clase(**campos)

        if tipo_campo is not None:
            hecho_traducido["tipo"] = tipo_campo

        # agregamos el hecho a la lista de hechos junto con sus campos
        hechos.append(hecho_traducido)

    return hechos


def _traducir_tipo(tipos: set[Node]) -> tuple[type[Fact] | None, str | None]:
    """
    Recibe un `set` de tipos (objetos del predicado RDF.type) y retorna la clase de hecho
    correspondiente, junto a un string tipo (valor del campo tipo de esa clase de hecho), si
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


def _traducir_campos(
    tripletas: Tripletas, datos: dict[Node, set[Node]]
) -> dict[str, Any]:
    """
    Recibe un diccionario de predicados con sus valores y retorna un diccionario de campos con
    sus respectivos valores para ser usados en una clase de hecho del sistema experto
    """

    campos = {}

    for pred, objs in datos.items():
        # print(f"\tTraduciendo predicado {pred}")
        # se traduce el predicado a un nombre de campo
        llave, valor = _traducir_campo(tripletas, pred, objs)
        campos[llave] = valor

    return campos


def _traducir_campo(
    tripletas: Tripletas, pred: Node, objs: set[Node]
) -> tuple[str, Any]:
    """
    Traduce un predicado con sus objetos de un grafo de ontologías a una tupla (campo, valor)
    para ser usado en la creación de un hecho del sistema experto

    Parámetros:
        - pred: un predicado de una tripleta en una ontología
        - objs: una lista de objetos asociados a dicho predicado
    Retorna:
        Una tupla con los siguientes valores:
        - el nombre del campo
        - el valor del atributo
    """

    match pred:
        case RUTA.nombre:
            return "nombre", _literal(objs)
        case RUTA.tipo:
            return "tipo", _literal(objs)
        case RUTA.via:
            return "via", _uri_ref_id(tripletas, objs)
        case RUTA.afectaVia:
            return "afecta_via", _uri_ref_id(tripletas, objs)
        case RUTA.seRelacionaCon:
            return "se_relaciona_con", _uri_ref_ids(tripletas, objs, id="numero")
        case RUTA.conectaCon:
            return "conecta_con", _uri_ref_ids(tripletas, objs)
        case RUTA.esConectada:
            return "es_conectada", _uri_ref_ids(tripletas, objs, id="numero")
        case RUTA.tiempoEspera:
            return "tiempo_espera", _literal(objs, xsd_type=XSD.double)
        case RUTA.intersectaCon:
            return "intersecta_con", _uri_ref_ids(tripletas, objs, id="numero")
        case RUTA.fluidez:
            return "fluidez", _literal(objs)
        case RUTA.velocidadPromedio:
            return "velocidad_promedio", _literal(objs, xsd_type=XSD.double)
        case RUTA.estaEnVia:
            return "via", _uri_ref_id(tripletas, objs)
        case RUTA.esBidireccional:
            return "es_bidireccional", _literal(objs, xsd_type=XSD.boolean)
        case DC.title:
            return "nombre", _literal(objs)
        case RUTA.tieneDistancia:
            return "distancia", _literal(objs)
        case RUTA.tieneVias:
            return "vias", _collection_ids(tripletas, objs)
        case RUTA.tiempoEstimado:
            return "tiempo_estimado", _literal(objs)
        case RUTA.cierreTotal:
            return "cierre_total", _literal(objs, xsd_type=XSD.boolean)
        case RUTA.duracion:
            return "duracion", _literal(objs, xsd_type=XSD.double)
        case RUTA.tieneNombre:
            return "nombre", _literal(objs)
        case RUTA.origen:
            return "origen", _bnode_id(tripletas, objs, "numero")
        case RUTA.destino:
            return "destino", _bnode_id(tripletas, objs, "numero")
        case RUTA.tieneNodos:
            return "tiene_nodos", _collection_ids(tripletas, objs, id="numero")
        case RUTA.numero:
            return "numero", _literal(objs)
        case RUTA.numeracion:
            return "numeracion", _literal(objs)
        case RUTA.afectadaPor:
            return "afectada_por", _uri_ref_ids(tripletas, objs, id="tipo")
        case RUTA.longitud:
            return "longitud", _literal(objs, xsd_type=XSD.double)
        case _:
            raise Exception(f"se encontró un predicado desconocido: {pred}")


def _literal(objs: set[Node], xsd_type=None) -> Any:
    """
    Retorna el valor del primer elemento de `objs` verificando que en realidad solo hay un elemento
    y que dicho elemento es un Literal

    Si se pasa el argumento `xsd_type` entonces busca entre los elementos de `objs` el que tenga el
    tipo indicado y lo retorna
    """
    if xsd_type is None:
        assert len(objs) == 1, f"len(objs) != 1, objs={objs}"
        obj = next(iter(objs))
        assert isinstance(obj, Literal)
        return obj.value

    for obj in objs:
        assert isinstance(obj, Literal)
        if obj.datatype == xsd_type:
            return obj.value

    raise Exception(f"no se encontró un elemento con ese xsd_type: {objs}")


def _uri_ref_id(tripletas: Tripletas, objs: set[Node], id="nombre") -> str:
    """
    Retorna el id del primer elemento de `objs` verificando que en realidad solo hay un
    elemento y que dicho elemento es un URIRef que además tiene un predicado RUTA:<id>
    """
    assert len(objs) == 1
    obj = next(iter(objs))
    assert isinstance(obj, URIRef)
    nombre = tripletas[obj][RUTA[id]]
    return _literal(nombre)


def _bnode_id(tripletas: Tripletas, objs: set[Node], id=None) -> str:
    """
    Retorna la representación en string del primer elemento de `objs` verificando que solo hay
    un elemento y que es un nodo blanco

    O retorna el id (RUTA:<id>) si id es diferente de None
    """
    assert len(objs) == 1
    obj = next(iter(objs))
    assert isinstance(obj, BNode)
    if id is None:
        return str(obj)
    return _nodo_id(tripletas, obj, id)


def _uri_ref_ids(tripletas: Tripletas, objs: set[Node], id="nombre") -> list[str]:
    """
    Retorna los ids de los elementos de `objs` verificando que dichos elementos son URIRef o BNode que además tienen un predicado RUTA:<id> si son URIRef
    """
    nombres = []
    for obj in objs:
        nombres.append(_nodo_id(tripletas, obj, id))
    return nombres


def _collection_ids(tripletas: Tripletas, objs: set[Node], id="nombre") -> list[str]:
    """
    Retorna una lista con los ids de los elementos de `objs` verificando que `objs` contenga
    una única collección cuyos elementos tengan valores para el predicado RUTA:<id> o sean nodos blancos
    """
    assert len(objs) == 1
    lista = next(iter(objs))
    assert isinstance(lista, BNode)

    # obtener los elementos de la colleción en una lista de python
    elementos = _recorrer_collection(tripletas, tripletas[lista])

    # obtener los RUTA:nombre de los elementos de la colleción
    elementos = list(map(lambda e: _nodo_id(tripletas, e, id), elementos))

    return elementos


def _nodo_id(tripletas: Tripletas, obj: Node, id="nombre") -> str:
    """
    Retorna el id (Ruta:<id>) asociado al sujeto `obj` o la representación en string de `obj` si id es None
    """
    if id is not None:
        nombre = tripletas[obj][RUTA[id]]
        return _literal(nombre)
    else:
        return str(obj)


def _recorrer_collection(tripletas: Tripletas, collection: Predicados) -> list[Node]:
    """
    Recorre la collección `collection` retornando una lista python equivalente (con elementos tipo URIRef o BNode)
    """
    resultado = []
    cur = collection
    while True:
        assert len(cur[RDF.first]) == 1, f"len(first) != 1, first: {cur[RDF.first]}"
        first = next(iter(cur[RDF.first]))

        assert isinstance(first, URIRef) or isinstance(first, BNode), f"first no es URIRef ni BNode, first: {first}"

        resultado.append(first)

        assert len(cur[RDF.rest]) == 1
        rest = next(iter(cur[RDF.rest]))

        if rest == RDF.nil:
            break
        cur = tripletas[rest]
    return resultado