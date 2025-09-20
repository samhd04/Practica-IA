import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from rdflib import Literal

# 1. Definir las variables difusas
# Variables de entrada
congestion = ctrl.Antecedent(np.arange(0, 101, 1), 'congestion')
velocidad_media = ctrl.Antecedent(np.arange(0, 61, 1), 'velocidad_media')
espera_semaforo = ctrl.Antecedent(np.arange(0, 181, 1), 'espera_semaforo')

# Variable de salida
fluidez = ctrl.Consequent(np.arange(0, 101, 1), 'fluidez')

# 2. Definir los conjuntos difusos y funciones de pertenencia
# Congestion (universo: 0-100)
congestion['baja'] = fuzz.trimf(congestion.universe, [0, 0, 40])
congestion['media'] = fuzz.trapmf(congestion.universe, [30, 45, 55, 70])
congestion['alta'] = fuzz.gaussmf(congestion.universe, 80, 8)

# Aplicar un modificador para Congestion: "muy" (intensificación)
congestion['muy_alta'] = fuzz.gaussmf(congestion.universe, 80, 8) ** 2

# VelocidadMedia (universo: 0-60)
velocidad_media['lenta'] = fuzz.gaussmf(velocidad_media.universe, 10, 4)
velocidad_media['normal'] = fuzz.trimf(velocidad_media.universe, [15, 30, 45])
velocidad_media['rapida'] = fuzz.trapmf(velocidad_media.universe, [40, 45, 60, 60])

# Aplicar un modificador para VelocidadMedia: "más o menos" (dilatación)
velocidad_media['mas_o_menos_normal'] = fuzz.trimf(velocidad_media.universe, [15, 30, 45]) ** 0.5

# EsperaSemaforo (universo: 0-180)
espera_semaforo['corta'] = fuzz.trapmf(espera_semaforo.universe, [0, 0, 11, 22])
espera_semaforo['media'] = fuzz.trimf(espera_semaforo.universe, [17, 33, 50])
espera_semaforo['larga'] = fuzz.gaussmf(espera_semaforo.universe, 67, 8)

# Fluidez (universo: 0-100)
fluidez['nula'] = fuzz.trimf(fluidez.universe, [0, 0, 10])
fluidez['muy_mala'] = fuzz.trimf(fluidez.universe, [5, 15, 25])
fluidez['mala'] = fuzz.trimf(fluidez.universe, [20, 35, 50])
fluidez['aceptable'] = fuzz.trimf(fluidez.universe, [45, 55, 65])
fluidez['buena'] = fuzz.trimf(fluidez.universe, [60, 75, 85])
fluidez['muy_buena'] = fuzz.trimf(fluidez.universe, [80, 100, 100])

# 3. Definir las reglas difusas
rule1 = ctrl.Rule(congestion['alta'] & velocidad_media['lenta'], fluidez['mala'])
rule2 = ctrl.Rule(congestion['muy_alta'], fluidez['muy_mala'])
rule3 = ctrl.Rule(congestion['baja'] & velocidad_media['rapida'], fluidez['buena'])
rule4 = ctrl.Rule(espera_semaforo['larga'] | congestion['alta'] | congestion['muy_alta'], fluidez['mala'])
rule5 = ctrl.Rule(~(congestion['alta'] | congestion['muy_alta']) & velocidad_media['normal'], fluidez['aceptable'])
rule6 = ctrl.Rule((congestion['baja'] | congestion['media']) & espera_semaforo['corta'], fluidez['buena'])
rule7 = ctrl.Rule(congestion['baja'] & espera_semaforo['corta'] & velocidad_media['rapida'], fluidez['muy_buena'])
rule8 = ctrl.Rule(velocidad_media['mas_o_menos_normal'], fluidez['aceptable'])
rule9 = ctrl.Rule(velocidad_media['rapida'] & espera_semaforo['corta'], fluidez['buena'])

# 4. Crear el sistema de control y simulación
sistema_control = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9])
simulacion_fluidez = ctrl.ControlSystemSimulation(sistema_control)

# 5. Proceso de defuzzificación

def calcular_fluidez_via(congestion_val, velocidad_val, espera_val):
    simulacion_fluidez.input['congestion'] = congestion_val
    simulacion_fluidez.input['velocidad_media'] = velocidad_val
    simulacion_fluidez.input['espera_semaforo'] = espera_val
    simulacion_fluidez.compute()

    salida = simulacion_fluidez.output['fluidez']

    # Mapear numérico a etiqueta del sistema experto
    if salida < 10:
        etiqueta = "nula"
    elif salida < 20:
        etiqueta = "muy mala"
    elif salida < 40:
        etiqueta = "mala"
    elif salida < 60:
        etiqueta = "aceptable"
    elif salida < 80:
        etiqueta = "buena"
    else:
        etiqueta = "muy buena"

    return etiqueta