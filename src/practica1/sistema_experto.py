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
        - tipo: calle | avenida | autopista | carrera
        - velocidad_media: un valor de tipo float en kilometros/hora
        - velocidad_maxima: un valor de tipo float en kilometros/hora
        - longitud: longitud de la vía en metros
        - fluidez: Muy mala | Mala | Aceptable | Buena | Muy buena
    """


class Nodo(Fact):
    """
    Representa un punto de referencia o una intersección
    Atributos:
        - tipo: Punto_de_referencia | intersección
        - nombre: Si es un punto de referencia, el nombre de este
        - vias_conectadas: Si es una intersección, las vías que esta conecta
        - se_relaciona_con: ... FIXME
        - intersecta_con: ... FIXME
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


# FIXME quitar esta clase de hecho:
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


class TiempoVia(Fact):
    """
    Representa el tiempo que toma atravesar una vía
    Atributos:
        - via: el nombre de la via
        - tiempo_estimado: tiempo en minutos que toma atravesar la via
    """


class TiempoRuta(Fact):
    """
    Representa el tiempo en minutos que se demoraría un carro en seguir una ruta
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

        # en self.__tiempos_via van a estar todos los hechos declarados de tipo TiempoVia (la llave es el nombre de la via)
        self.__tiempos_via = {}

        super().__init__()

    def declare(self, *facts):
        # Iterar sobre todos los hechos a declarar, agregándolos a self.__vias si son de tipo Via y
        # a self.__rutas si son de tipo Ruta
        for fact in facts:
            if isinstance(fact, Via):
                self.__vias[fact["nombre"]] = fact
            elif isinstance(fact, Ruta):
                self.__rutas[fact["nombre"]] = fact
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
        # FIXME: definir esto
        fluidez = {"choque": "muy mala", "obra": "mala", "manifestación": "nula"}[tipo]
        print(f"Fluidez {fluidez} debido a {tipo} en la vía {via}")
        self.declare(Fluidez(fluidez=fluidez, via=via))

    @Rule(
        Via(
            nombre=MATCH.nombre,
            velocidad_media=MATCH.velocidad_media,
            longitud=MATCH.longitud,
        ),
        NOT(TiempoVia(via=MATCH.nombre)),
    )
    def calcular_tiempo_via(self, nombre, velocidad_media, longitud):
        """
        Cálculo inicial del tiempo estimado que toma atravesar una via
        """
        # FIXME: corregir este calculo teniendo en cuenta las unidades
        tiempo = longitud / velocidad_media
        print(f"Cálculo inicial de tiempo estimado para via {nombre}: {tiempo}")
        hecho = self.declare(TiempoVia(via=nombre, tiempo_estimado=tiempo))
        self.__tiempos_via[nombre] = hecho

    @Rule(
        TiempoVia(via=MATCH.via_nombre, tiempo_estimado=MATCH.tiempo),
        Semaforo(via=MATCH.via_nombre, tiempo_espera=MATCH.tiempo_semaforo),
    )
    def agregar_tiempos_semaforos(self, via_nombre, tiempo, tiempo_semaforo):
        """
        Agrega el tiempo que se demoran los semáforos al tiempo estimado de atravesar la vía
        """
        nuevo_tiempo = tiempo + tiempo_semaforo
        print(
            f"Cálculo (incluyendo semaforos) de tiempo estimado para via {via_nombre}: {nuevo_tiempo}"
        )
        tiempo_via = self.__tiempos_via[via_nombre]
        self.modify(tiempo_via, tiempo_estimado=nuevo_tiempo)

    @Rule(
        TiempoVia(via=MATCH.via_nombre, tiempo_estimado=MATCH.tiempo),
        Evento(afecta_via=MATCH.via_nombre, tipo=MATCH.evento_tipo),
    )
    def agregar_tiempos_eventos(self, via_nombre, tiempo, evento_tipo):
        """
        Agrega el tiempo que se demoran los semáforos al tiempo estimado de atravesar la vía
        """
        # FIXME: definir estos valores
        tiempo_adicional = {"choque": 20, "obra": 10, "manifestación": 999}[evento_tipo]
        nuevo_tiempo = tiempo + tiempo_adicional
        print(
            f"Cálculo (incluyendo {evento_tipo}) de tiempo estimado para via {via_nombre}: {nuevo_tiempo}"
        )
        tiempo_via = self.__tiempos_via[via_nombre]
        self.modify(tiempo_via, tiempo_estimado=nuevo_tiempo)

    @Rule(
        Ruta(nombre=MATCH.nombre, vias=MATCH.vias), NOT(TiempoRuta(ruta=MATCH.nombre))
    )
    def calcular_tiempo_ruta(self, nombre, vias):
        """
        Regla que calcula el tiempo estimado de cada ruta
        """
        tiempo_estimado = 0

        for via_nombre in vias:
            tiempo_via = self.__tiempos_via[via_nombre]
            tiempo_estimado += tiempo_via["tiempo_estimado"]

        self.declare(TiempoRuta(ruta=nombre, tiempo_estimado=tiempo_estimado))

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
