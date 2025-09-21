"""
Sistema experto, contiene definiciones de clases de hechos y el motor de inferencia con sus reglas
"""

from collections import defaultdict
from math import inf
from experta import MATCH, Fact, KnowledgeEngine, Rule, NOT
import random

from numpy import isin

from practica1.sistema_logica_difusa import calcular_fluidez_via

random.seed(42)


class Via(Fact):
    """
    Representa una vía por la cual transitan carros
    Atributos:
        - nombre: el nombre de la vía
        - tipo: calle | avenida | autopista | carrera | transversal
        - velocidad_promedio: un valor de tipo float en kilómetros/hora
        - longitud: longitud de la vía en kilómetros
        - afectada_por: una lista de tipos de eventos que afectan esta via
        - es_bidireccional: True si esta via es bidireccional
    """


class Nodo(Fact):
    """
    Representa un punto de referencia o una intersección
    Atributos:
        - tipo: Punto_de_referencia | intersección
        - nombre: Si es un punto de referencia, el nombre de este
        - numero: el numero de la intersección si este nodo es una intersección
        - vias_conectadas: Si es una intersección, las vías que esta conecta
        - se_relaciona_con: intersecciones con las cuales este nodo se relaciona si este nodo es un punto de referencia
        - intersecta_con: otras intersecciones con las que este nodo intersecta si este nodo es una intersección
        - conecta_con: una lista de nombres de vias con las cuales se conecta este nodo si es una intersección
    """


class Semaforo(Fact):
    """
    Atributos:
        - tiempo_espera: valor de tipo entero, tiempo en segundos que el semaforo está en rojo
        - via: el nombre de la vía en la que el semanforo se encuentra
    """


class Evento(Fact):
    """
    Representa un evento que está afectando una vía
    Atributos:
        - tipo: Vehiculo Detenido | Obra Vial | Obra Menor | Manifestacion | Accidente Leve | Accidente Grave | Colapso Estructural
        - afecta_via: el nombre de la via que es afectada por este evento
        - cierre_total: indica si este evento causa un cierre total (True/False)
        - duracion: tiempo en minutos que este evento afecta la via
    """


class Ruta(Fact):
    """
    Representa una ruta (un conjunto ordenado de vías) que un carro puede seguir
    Atributos:
        - numeracion: el nombre de la ruta
        - tiene_nodos: lista de intersecciones por donde pasa la ruta (los numeros de las intersecciones)
        - vias: lista de vias por donde pasa la ruta (los nombres de las vias)
        - origen: el nodo donde inicia la ruta (el numero de la intersección)
        - destino: el nodo donde termina la ruta (el numero de la intersección)
        - distancia: la distancia total que recorre esta ruta FIXME: eliminar esta?
    """


# FIXME: si es necesaria esta clase?
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


class TiempoVia(Fact):
    """
    Representa el tiempo que toma atravesar una vía
    Atributos:
        - via: el nombre de la via
        - tiempo_estimado: tiempo en minutos que toma atravesar la via
        - incluye_tiempos_semaforo: True si los incluye
        - incluye_tiempos_eventos: True si los incluye
        - incluye_tiempos_fluidez: True si los incluye
        - incluye_bonificacion_bidireccional: True si la incluye
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

        # en self.__rutas van a estar todos los hechos declarados de tipo Ruta (la llave es la numeracion de la ruta)
        self.__rutas = {}

        # en self.__intersecciones van a estar todos los hechos declarados de tipo Nodo que son
        # intersección (la llave es el numero de la intersección)
        self.__intersecciones = {}

        # en self.__puntos_de_referencia van a estar todos los hechos declarados de tipo Nodo que son
        # puntos de referencia (la llave es el nombre del punto)
        self.__puntos_de_referencia = {}

        # en self.__tiempos_via van a estar todos los hechos declarados de tipo TiempoVia (la llave es el nombre de la via)
        self.__tiempos_via = {}

        # en self.__tiempos_ruta van a estar todos los hechos declarados de tipo TiempoRuta (la llave es la numeracion de la ruta)
        self.__tiempos_ruta = {}

        super().__init__()

    def declare(self, *facts):
        # Iterar sobre todos los hechos a declarar, agregándolos a self.__vias si son de tipo Via y
        # a self.__rutas si son de tipo Ruta
        for fact in facts:
            if isinstance(fact, Via):
                self.__vias[fact["nombre"]] = fact
            elif isinstance(fact, Ruta):
                self.__rutas[fact["numeracion"]] = fact
            elif isinstance(fact, Nodo):
                if "nombre" in fact:
                    self.__puntos_de_referencia[fact["nombre"]] = fact
                elif "numero" in fact:
                    self.__intersecciones[fact["numero"]] = fact
        return super().declare(*facts)

    @Rule(
        Evento(cierre_total=True, tipo=MATCH.evento_tipo),
        Via(nombre=MATCH.via_nombre, afectada_por=MATCH.via_afectada_por),
        salience=30,
    )
    def evento_cierre_total(self, via_nombre, evento_tipo, via_afectada_por):
        """
        Esta regla elimina las vias que están afectadas por un evento de cierre total
        También elimina todas las rutas que contienen esas vias eliminadas
        """
        # Si este evento no afecta la via, no continuar la ejecución de esta regla
        if evento_tipo not in via_afectada_por:
            return

        print(
            f"Eliminando via {via_nombre} pues está afectada por evento de cierre total: {evento_tipo}"
        )
        self.retract(self.__vias[via_nombre])
        del self.__vias[via_nombre]

        rutas_eliminadas = []
        for ruta_numeracion, ruta in self.__rutas.items():
            if via_nombre in ruta["vias"]:
                print(
                    f"También eliminando la ruta {ruta_numeracion} que contiene via con cierre total"
                )
                self.retract(ruta)
                rutas_eliminadas.append(ruta_numeracion)

        for ruta in rutas_eliminadas:
            del self.__rutas[ruta]

    @Rule(
        Ruta(numeracion=MATCH.ruta_numeracion, origen=MATCH.ruta_origen),
        Nodo(
            tipo="Punto_de_referencia",
            nombre=MATCH.punto_nombre,
            se_relaciona_con=MATCH.punto_se_relaciona_con,
        ),
        Objetivo(desde=MATCH.punto_nombre),
        salience=20,
    )
    def ruta_que_no_inicia_en_objetivo(
        self, ruta_numeracion, ruta_origen, punto_se_relaciona_con
    ):
        """
        Regla que elimina todas las rutas que inician en una intersección que no se relaciona con
        el punto de partida deseado
        """
        # si la ruta inicia en el punto de referencia deseado
        if ruta_origen in punto_se_relaciona_con:
            print(
                f"La ruta {ruta_numeracion} sirve (inicia en el punto de origen deseado)"
            )
        else:
            print(
                f"Eliminando ruta {ruta_numeracion} debido a que no inicia en el punto de partida deseado"
            )
            self.retract(self.__rutas[ruta_numeracion])
            del self.__rutas[ruta_numeracion]

    @Rule(
        Ruta(numeracion=MATCH.ruta_numeracion, destino=MATCH.ruta_destino),
        Nodo(
            tipo="Punto_de_referencia",
            nombre=MATCH.punto_nombre,
            se_relaciona_con=MATCH.punto_se_relaciona_con,
        ),
        Objetivo(hasta=MATCH.punto_nombre),
        salience=20,
    )
    def ruta_que_no_termina_en_objetivo(
        self, ruta_numeracion, ruta_destino, punto_se_relaciona_con
    ):
        """
        Regla que elimina todas las rutas que terminan en una intersección que no se relaciona con
        el punto de llegada deseado
        """
        # si la ruta termina en el punto de referencia deseado
        if ruta_destino in punto_se_relaciona_con:
            print(
                f"La ruta {ruta_numeracion} sirve (termina en el punto de llegada deseado)"
            )
        else:
            print(
                f"Eliminando ruta {ruta_numeracion} debido a que no termina en el punto de llegada deseado"
            )
            self.retract(self.__rutas[ruta_numeracion])
            del self.__rutas[ruta_numeracion]

    @Rule(
        Via(
            nombre=MATCH.nombre,
            velocidad_promedio=MATCH.velocidad_promedio,
            longitud=MATCH.longitud,
        ),
        NOT(TiempoVia(via=MATCH.nombre)),
        salience=4,
    )
    def calcular_tiempo_via(self, nombre, velocidad_promedio, longitud):
        """
        Cálculo inicial del tiempo estimado que toma atravesar una via
        """
        tiempo = longitud / velocidad_promedio
        print(f"Cálculo inicial de tiempo estimado para via {nombre}: {tiempo} horas")
        hecho = self.declare(TiempoVia(via=nombre, tiempo_estimado=tiempo))
        self.__tiempos_via[nombre] = hecho

    @Rule(
        TiempoVia(via=MATCH.via_nombre, tiempo_estimado=MATCH.tiempo),
        Semaforo(via=MATCH.via_nombre, tiempo_espera=MATCH.tiempo_semaforo),
        NOT(TiempoVia(via=MATCH.via_nombre, incluye_tiempos_semaforo=True)),
        salience=3,
    )
    def agregar_tiempos_semaforos(self, via_nombre, tiempo, tiempo_semaforo):
        """
        Agrega el tiempo que se demoran los semáforos al tiempo estimado de atravesar la vía
        """
        # El nuevo tiempo será el tiempo anterior sumado al tiempo del semaforo convertido de
        # segundos a horas
        nuevo_tiempo = tiempo + (tiempo_semaforo / 60 / 60)
        print(
            f"Cálculo (incluyendo semaforos) de tiempo estimado para via {via_nombre}: {nuevo_tiempo} horas"
        )
        tiempo_via = self.__tiempos_via[via_nombre]
        tiempo_via = self.modify(
            tiempo_via, tiempo_estimado=nuevo_tiempo, incluye_tiempos_semaforo=True
        )
        self.__tiempos_via[via_nombre] = tiempo_via

    @Rule(
        TiempoVia(via=MATCH.via_nombre, tiempo_estimado=MATCH.tiempo),
        Via(nombre=MATCH.via_nombre, afectada_por=MATCH.via_afectada_por),
        Evento(tipo=MATCH.evento_tipo, duracion=MATCH.evento_duracion),
        NOT(TiempoVia(via=MATCH.via_nombre, incluye_tiempos_eventos=True)),
        salience=3,
    )
    def agregar_tiempos_eventos(
        self, via_nombre, via_afectada_por, tiempo, evento_tipo, evento_duracion
    ):
        """
        Agrega el tiempo que se demoran los eventos al tiempo estimado de atravesar la vía
        """
        # verificar si el evento afecta esta via
        evento_afecta_via = False
        for evento in via_afectada_por:
            if evento == evento_tipo:
                evento_afecta_via = True
                break

        if not evento_afecta_via:
            return

        # el nuevo tiempo será el tiempo anterior sumado a la duración del evento convertido de
        # minutos a horas
        nuevo_tiempo = tiempo + (evento_duracion / 60)
        print(
            f"Cálculo (incluyendo {evento_tipo}) de tiempo estimado para via {via_nombre}: {nuevo_tiempo}"
        )
        tiempo_via = self.__tiempos_via[via_nombre]
        tiempo_via = self.modify(
            tiempo_via, tiempo_estimado=nuevo_tiempo, incluye_tiempos_eventos=True
        )
        self.__tiempos_via[via_nombre] = tiempo_via

    @Rule(
        Ruta(numeracion=MATCH.numeracion, vias=MATCH.vias),
        NOT(TiempoRuta(ruta=MATCH.numeracion)),
    )
    def calcular_tiempo_ruta(self, numeracion, vias):
        """
        Regla que calcula el tiempo estimado de cada ruta
        """
        tiempo_estimado = 0

        for via_nombre in vias:
            tiempo_via = self.__tiempos_via[via_nombre]
            tiempo_estimado += tiempo_via["tiempo_estimado"]

        print(f"Tiempo de la ruta {numeracion} calculado: {tiempo_estimado}")
        tiempo_ruta = self.declare(
            TiempoRuta(ruta=numeracion, tiempo_estimado=tiempo_estimado)
        )
        self.__tiempos_ruta[numeracion] = tiempo_ruta

    @Rule(
        Via(nombre=MATCH.via_nombre, velocidad_promedio=MATCH.velocidad),
        Semaforo(via=MATCH.via_nombre),
        salience=7
    )
    def calcular_fluidez_con_semaforo(self, via_nombre, velocidad):
        """
        Regla para calcular fluidez cuando la vía tiene semáforo.
        La espera del semáforo se genera de forma aleatoria (30–120 segundos).
        """
        congestion_val = random.randint(0, 100)  # Congestión aleatoria
        espera_val = random.randint(30, 120)  # Espera en segundos (Colombia)

        fluidez_literal = calcular_fluidez_via(congestion_val, velocidad, espera_val)

        print(
            f"Fluidez de la via {via_nombre} (con semáforo) calculada: {fluidez_literal}"
        )
        self.declare(Fluidez(via=via_nombre, fluidez=str(fluidez_literal)))

    @Rule(
        Via(nombre=MATCH.via_nombre, velocidad_promedio=MATCH.velocidad),
        NOT(Semaforo(via=MATCH.via_nombre)),
        salience=7
    )
    def calcular_fluidez_sin_semaforo(self, via_nombre, velocidad):
        """
        Regla para calcular fluidez cuando la vía no tiene semáforo.
        Espera en semáforo = 0.
        """
        congestion_val = random.randint(0, 100)  # Congestión aleatoria
        espera_val = 0  # No hay semáforo

        fluidez_literal = calcular_fluidez_via(congestion_val, velocidad, espera_val)

        print(
            f"Fluidez de la via {via_nombre} (sin semáforo) calculada: {fluidez_literal}"
        )
        self.declare(Fluidez(via=via_nombre, fluidez=str(fluidez_literal)))

    @Rule(Fluidez(fluidez="nula", via=MATCH.via), salience=6)
    def fluidez_nula(self, via):
        """
        Regla que elimina las vias con fluidez nula, y por lo tanto también elimina todas las rutas
        que transitan esa vía eliminada
        """
        print(f"Eliminando via {via} debido a que presenta una fluidez nula")
        self.retract(self.__vias[via])
        del self.__vias[via]

        for ruta_numeracion, ruta in self.__rutas.items():
            if via in ruta["vias"]:
                print(
                    f"\tTambién eliminando ruta {ruta_numeracion} que contiene via con fluidez nula"
                )
                self.retract(ruta)
                del self.__rutas[ruta_numeracion]

    @Rule(
        Fluidez(via=MATCH.via_nombre, fluidez=MATCH.fluidez_val),
        TiempoVia(via=MATCH.via_nombre, tiempo_estimado=MATCH.tiempo),
        NOT(TiempoVia(via=MATCH.via_nombre, incluye_tiempos_fluidez=True)),
        salience=2
    )
    def ajustar_tiempo_por_fluidez(self, via_nombre, fluidez_val, tiempo):
        """
        Ajusta el tiempo de las vías según la fluidez:
        - muy mala  → +80%
        - mala      → +40%
        - aceptable → +10%
        - buena     → -10%
        - muy buena → -20%
        """
        factor = {
            "muy mala": 1.8,
            "mala": 1.4,
            "aceptable": 1.1,
            "buena": 0.9,
            "muy buena": 0.8,
        }.get(fluidez_val, 1.0)  # por defecto no cambia

        if factor != 1.0:
            nuevo_tiempo = tiempo * factor
            print(
                f"Ajustando tiempo de via {via_nombre} por fluidez {fluidez_val}: "
                f"{tiempo} → {nuevo_tiempo}"
            )
            tiempo_via = self.__tiempos_via[via_nombre]
            tiempo_via = self.modify(tiempo_via, tiempo_estimado=nuevo_tiempo, incluye_tiempos_fluidez=True)
            self.__tiempos_via[via_nombre] = tiempo_via

    @Rule(
        Via(nombre=MATCH.via_nombre, es_bidireccional=True),
        TiempoVia(via=MATCH.via_nombre, tiempo_estimado=MATCH.tiempo),
        NOT(TiempoVia(via=MATCH.via_nombre, incluye_bonificacion_bidireccional=True)),
        salience=3
    )
    def bonificar_vias_bidireccionales(self, via_nombre, tiempo):
        """
        Reduce en un 10% el tiempo estimado de vías bidireccionales
        """
        nuevo_tiempo = tiempo * 0.9
        print(f"Reduciendo tiempo de via {via_nombre} por ser bidireccional: {nuevo_tiempo}")
        tiempo_via = self.__tiempos_via[via_nombre]
        tiempo_via = self.modify(tiempo_via, tiempo_estimado=nuevo_tiempo, incluye_bonificacion_bidireccional=True)
        self.__tiempos_via[via_nombre] = tiempo_via

    @Rule()
    def regla15(self):
        pass

    @Rule(NOT(Fact()))
    def recomendacion_final(self):
        mejor_ruta = None
        mejor_ruta_tiempo = inf
        for ruta_numeracion, ruta in self.__rutas.items():
            tiempo_ruta = self.__tiempos_ruta[ruta_numeracion]
            tiempo = tiempo_ruta["tiempo_estimado"]
            if tiempo < mejor_ruta_tiempo:
                mejor_ruta = ruta
                mejor_ruta_tiempo = tiempo

        if mejor_ruta is None:
            print("No fue posible encontrar la mejor ruta")
            return

        print(f"La mejor ruta es: {mejor_ruta['numeracion']}")
        for via in mejor_ruta["vias"]:
            print(f"\t{via}")
        print("Pasando por las intersecciones:")
        for interseccion_numero in mejor_ruta["tiene_nodos"]:
            interseccion = self.__intersecciones[interseccion_numero]
            print(f"\t{interseccion_numero} ({list(interseccion['conecta_con'])})")
