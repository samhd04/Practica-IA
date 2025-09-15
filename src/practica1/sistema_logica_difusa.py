import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

# 1. Definir las variables difusas
# Variables de entrada
congestion = ctrl.Antecedent(np.arange(0, 101, 1), 'congestion')
velocidad_media = ctrl.Antecedent(np.arange(0, 61, 1), 'velocidad_media')

# Variable de salida
espera_semaforo = ctrl.Consequent(np.arange(0, 181, 1), 'espera_semaforo')

# 2. Definir los conjuntos difusos y funciones de pertenencia
# Congestion (universo: 0-100)
congestion['baja'] = fuzz.trimf(congestion.universe, [0, 0, 40])
congestion['media'] = fuzz.trapmf(congestion.universe, [30, 45, 55, 70])
congestion['alta'] = fuzz.gaussmf(congestion.universe, 80, 8)

# Aplicar un modificador para Congestion: "muy" (intensificación)
# Esto se logra elevando la función de pertenencia a una potencia > 1
congestion['muy_alta'] = fuzz.gaussmf(congestion.universe, 80, 8) ** 2

# VelocidadMedia (universo: 0-60)
velocidad_media['lenta'] = fuzz.gaussmf(velocidad_media.universe, 10, 4)
velocidad_media['normal'] = fuzz.trimf(velocidad_media.universe, [15, 30, 45])
velocidad_media['rapida'] = fuzz.trapmf(velocidad_media.universe, [40, 45, 60, 60])

# Aplicar un modificador para VelocidadMedia: "más o menos" (dilatación)
# Esto se logra elevando la función de pertenencia a una potencia < 1
velocidad_media['mas_o_menos_normal'] = fuzz.trimf(velocidad_media.universe, [15, 30, 45]) ** 0.5

# EsperaSemaforo (universo: 0-180)
espera_semaforo['corta'] = fuzz.trapmf(espera_semaforo.universe, [0, 0, 20, 40])
espera_semaforo['media'] = fuzz.trimf(espera_semaforo.universe, [30, 60, 90])
espera_semaforo['larga'] = fuzz.gaussmf(espera_semaforo.universe, 120, 15)

# 3. Definir las reglas difusas (mínimo 9 reglas)
rule1 = ctrl.Rule(congestion['baja'] & velocidad_media['rapida'], espera_semaforo['corta'])
rule2 = ctrl.Rule(congestion['media'] | velocidad_media['normal'], espera_semaforo['media'])
rule3 = ctrl.Rule(congestion['alta'] & velocidad_media['lenta'], espera_semaforo['larga'])
rule4 = ctrl.Rule(congestion['alta'] & ~velocidad_media['rapida'], espera_semaforo['larga'])
rule5 = ctrl.Rule(congestion['baja'] | ~velocidad_media['lenta'], espera_semaforo['corta'])
rule6 = ctrl.Rule(congestion['media'] & ~velocidad_media['normal'], espera_semaforo['media'])
rule7 = ctrl.Rule(congestion['muy_alta'] & velocidad_media['lenta'], espera_semaforo['larga'])
rule8 = ctrl.Rule(congestion['baja'] & velocidad_media['mas_o_menos_normal'], espera_semaforo['media'])
rule9 = ctrl.Rule(~congestion['baja'] & velocidad_media['normal'], espera_semaforo['media'])

# 4. Crear el sistema de control y simulación
sistema_control = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9])
simulacion_espera = ctrl.ControlSystemSimulation(sistema_control)

# 5. Proceso de defuzzificación (ejemplo justificado)
# Scikit-fuzzy utiliza el método del "centroide" por defecto, que calcula el centro de masa del área.
# Es un método robusto y comúnmente utilizado que representa bien el resultado global.
print("El método de defuzzificación por defecto en scikit-fuzzy es el centroide.")
print("Este método es preferido por su precisión al calcular el 'centro de masa' de la salida.")

# 6. Realizar una simulación con valores de ejemplo
simulacion_espera.input['congestion'] = 75
simulacion_espera.input['velocidad_media'] = 25

simulacion_espera.compute()

# Mostrar los resultados
print("\n--- Resultados de la simulación ---")
print(f"Congestión de entrada: 75")
print(f"Velocidad Media de entrada: 25")
print(f"Espera del semáforo (salida): {simulacion_espera.output['espera_semaforo']:.2f} segundos")

# Opcional: Visualizar los resultados
congestion.view(sim=simulacion_espera)
velocidad_media.view(sim=simulacion_espera)
espera_semaforo.view(sim=simulacion_espera)

plt.show()