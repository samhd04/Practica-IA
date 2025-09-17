"""
Sistema experto, contiene definiciones de clases de hechos y el motor de inferencia con sus reglas
"""

from collections import defaultdict
from experta import MATCH, Fact, KnowledgeEngine, Rule, NOT


class Via(Fact):
    """
    Representa una vía por la cual transitan carros
    Atributos:
        - nombre: el nombre de la vía
        - tipo: calle | avenida | autopista
        - velocidad_media: un valor de tipo float en metros/minuto
        - longitud: longitud de la vía en metros
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


class Objetivo(Fact):
    """
    Representa el objetivo del usuario (desde dónde quiere partir y adónde quiere llegar)
    Atributos:
        - desde: lugar de partida (nombre de un punto de referencia)
        - hasta: lugar al que se desea llegar (nombre de un punto de referencia)
    """


class TiempoRuta(Fact):
    """
    Representa
    Atributos:
        - ruta: el nombre de la ruta
        - tiempo_estimado: tiempo en minutos que toma atravesar la ruta
    """


class Motor(KnowledgeEngine):
    def __init__(self):
        # en self.__vias van a estar todos los hechos declarados de tipo Via (la llave es el nombre de la via)
        self.__vias = {}

        # en self.__rutas van a estar todos los hechos declarados de tipo Ruta (la llave es el nombre de la ruta)
        self.__rutas = {}

        # en self.__semaforos van a estar todos los hechos declarados de tipo Semaforo
        # (la llave es el nombre de la vía en la que se encuentra el semaforo y el valor es una
        # lista de semafaros en esa vía)
        self.__semaforos = defaultdict(list)

        super().__init__()

    def declare(self, *facts):
        # Iterar sobre todos los hechos a declarar, agregándolos a self.__vias si son de tipo Via,
        # a self.__rutas si son de tipo Ruta y a self.__semaforos si son tipo Semaforo
        for fact in facts:
            if isinstance(fact, Via):
                self.__vias[fact["nombre"]] = fact
            elif isinstance(fact, Ruta):
                self.__rutas[fact["nombre"]] = fact
            elif isinstance(fact, Semaforo):
                self.__semaforos[fact["via"]].append(fact)
        return super().declare(*facts)

    @Rule(Fluidez(fluidez="nula", via=MATCH.via), salience=4)
    def fluidez_nula(self, via):
        """
        Regla que elimina las vias con fluidez nula, y por lo tanto también elimina todas las rutas
        que transitan esa vía eliminada
        """
        print(f"Eliminando via {via} debido a que presenta una fluidez nula")
        self.retract(self.__vias[via])

        for ruta_nombre, ruta in self.__rutas.items():
            if via in ruta["vias"]:
                print(f"\tTambién eliminando ruta {ruta_nombre} que contiene esta via")
                self.retract(ruta)

    @Rule(
        Ruta(nombre=MATCH.ruta_nombre, vias=MATCH.ruta_vias),
        Nodo(
            tipo="Punto_de_referencia",
            nombre=MATCH.punto_nombre,
            vias_conectadas=MATCH.punto_vias_conectadas,
        ),
        Objetivo(desde=MATCH.punto_nombre),
        salience=3,
    )
    def ruta_que_no_inicia_en_objetivo(
        self, ruta_nombre, ruta_vias, punto_vias_contectadas
    ):
        """
        Regla que elimina todas las rutas que inician en una vía que no contiene el punto de
        partida deseado
        """
        ruta_sirve = False
        for via in punto_vias_contectadas:
            if via == ruta_vias[0]:
                ruta_sirve = True
                break

        if not ruta_sirve:
            print(
                f"Eliminando ruta {ruta_nombre} debido a que no inicia en el punto de partida deseado"
            )
            self.retract(self.__rutas[ruta_nombre])

    @Rule(
        Ruta(nombre=MATCH.ruta_nombre, vias=MATCH.ruta_vias),
        Nodo(
            tipo="Punto_de_referencia",
            nombre=MATCH.punto_nombre,
            vias_conectadas=MATCH.punto_vias_conectadas,
        ),
        Objetivo(hasta=MATCH.punto_nombre),
        salience=3,
    )
    def ruta_que_no_termina_en_objetivo(
        self, ruta_nombre, ruta_vias, punto_vias_contectadas
    ):
        """
        Regla que elimina todas las rutas que terminan en una vía que no contiene el punto de
        llegada deseado
        """
        ruta_sirve = False
        for via in punto_vias_contectadas:
            if via == ruta_vias[-1]:
                ruta_sirve = True
                break

        if not ruta_sirve:
            print(
                f"Eliminando ruta {ruta_nombre} debido a que no termina en el punto de llegada deseado"
            )
            self.retract(self.__rutas[ruta_nombre])

    @Rule(Evento(tipo=MATCH.tipo, afecta_via=MATCH.via), salience=3)
    def evento_en_via(self, tipo, via):
        fluidez = {"choque": "muy mala", "obra": "mala", "manifestación": "nula"}[tipo]
        print(f"Fluidez {fluidez} debido a {tipo} en la vía {via}")
        self.declare(Fluidez(fluidez=fluidez, via=via))

    @Rule(
        Ruta(nombre=MATCH.nombre, vias=MATCH.vias), NOT(TiempoRuta(ruta=MATCH.nombre))
    )
    def temporizar_ruta(self, nombre, vias):
        """
        Regla que calcula el tiempo estimado de cada ruta
        """
        tiempo_estimado = 0

        for via_nombre in vias:
            via = self.__vias[via_nombre]
            # FIXME: mejorar esto
            tiempo = via["longitud"] / via["velocidad_media"]
            for semaforo in self.__semaforos[via_nombre]:
                tiempo += semaforo["tiempo_espera"]
            tiempo_estimado += tiempo

        self.declare(TiempoRuta(ruta=nombre, tiempo_estimado=tiempo_estimado))

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
