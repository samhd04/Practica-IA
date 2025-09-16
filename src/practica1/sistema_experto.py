"""
Sistema experto, contiene definiciones de clases de hechos y el motor de inferencia con sus reglas
"""

from experta import MATCH, Fact, KnowledgeEngine, Rule


class Via(Fact):
    """
    Representa una vía por la cual transitan carros
    Atributos:
        - nombre: el nombre de la vía
        - tipo: calle | avenida | autopista
        - velocidad_media: un valor de tipo float
    """


class Nodo(Fact):
    """
    Representa un punto de referencia o una intersección
    Atributos:
        - tipo: Punto_de_referencia | intersección
        - nombre: Si es un punto de referencia, el nombre de este
        - vias_conectadas: Si es una intersección, las vías que esta conecta
    """


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


class Fluidez(Fact):
    """
    Representa la fluidez de una vía
    Atributos:
        - fluidez: nula | muy mala | mala | aceptable | buena | muy buena
        - via: el nombre de la via con esta fluidez
    """


class Motor(KnowledgeEngine):
    def __init__(self):
        self._vias = {}
        super().__init__()

    def declare(self, *facts):
        for fact in facts:
            if isinstance(fact, Via):
                self._vias[fact["nombre"]] = fact
        return super().declare(*facts)

    @Rule(Fluidez(fluidez="nula", via=MATCH.via), salience=4)
    def fluidez_nula(self, via):
        print(f"Eliminando via {via} debido a que presenta una fluidez nula")
        self.retract(self._vias[via])

    @Rule(Evento(tipo=MATCH.tipo, afecta_via=MATCH.via), salience=3)
    def evento_en_via(self, tipo, via):
        fluidez = {"choque": "muy mala", "obra": "mala", "manifestación": "nula"}[tipo]
        print(f"Fluidez {fluidez} debido a {tipo} en la vía {via}")
        self.declare(Fluidez(fluidez=fluidez, via=via))

    @Rule()
    def regla3(self):
        pass

    @Rule()
    def regla4(self):
        pass

    @Rule()
    def regla5(self):
        pass

    @Rule()
    def regla6(self):
        pass

    @Rule()
    def regla7(self):
        pass

    @Rule()
    def regla8(self):
        pass

    @Rule()
    def regla9(self):
        pass

    @Rule()
    def regla10(self):
        pass

    @Rule()
    def regla11(self):
        pass

    @Rule()
    def regla12(self):
        pass

    @Rule()
    def regla13(self):
        pass

    @Rule()
    def regla14(self):
        pass

    @Rule()
    def regla15(self):
        pass
