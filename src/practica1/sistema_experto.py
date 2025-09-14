"""
Sistema experto, contiene definiciones de clases de hechos y el motor de inferencia con sus reglas
"""

from experta import Fact, KnowledgeEngine


class Via(Fact):
    """
    Representa una vía por la cual transitan carros
    Atributos:
        - nombre: el nombre de la vía
        - tipo: calle | avenida | autopista
        - velocidad_media: un valor de tipo float
        - fluidez: nula | muy mala | mala | aceptable | buena | muy buena
    """

    pass


class Nodo(Fact):
    """
    Representa un punto de referencia o una intersección
    Atributos:
        - tipo: Punto_de_referencia | intersección
        - nombre: Si es un punto de referencia, el nombre de este
        - vias_conectadas: Si es una intersección, las vías que esta conecta
    """

    pass


class Semaforo(Fact):
    """
    Atributos:
        - tiempo_espera: valor de tipo entero, tiempo en minutos que el semaforo está en rojo
        - via: el nombre de la vía en la que el semanforo se encuentra
    """


class Evento(Fact):
    """
    Representa un evento que está afectando una vía
    Atributos:
        - tipo: choque | obra | manifestación
        - afecta_via: el nombre de la via que es afectada por este evento
    """


class Ruta(Fact):
    """
    Representa una ruta (un conjunto ordenado de vías) que un carro puede seguir
    Atributos:
        - nombre: el nombre de la ruta
        - vias: lista de nombres de vías
        - distancia: la distancia total que recorre esta ruta
        - tiempo_estimado: tiempo en minutos que se demoraría un carro en seguir esta ruta
    """


class Recomendacion(Fact):
    """
    Representa la recomendación de ruta que el sistema experto entrega
    Atributos:
        - origen: el nombre del punto de referencia desde el que se parte
        - destino: el nombre del punto de referencia al que se llega
        - ruta: el nombre de la ruta recomendada
        - fluidez
        - tiempo_estimado: tiempo en minutos que toma seguir la ruta
    """


class Motor(KnowledgeEngine):
    pass
