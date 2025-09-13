import collections.abc

# Parche por fallos en importación de experta
if not hasattr(collections, "Mapping"):
    setattr(collections, "Mapping", collections.abc.Mapping)

from practica1.ontologia import g
from practica1.sistema_experto import Motor
from practica1.traductor_ontologia import traducir


def main() -> None:
    motor = Motor()
    motor.reset()

    for hecho in traducir(g):
        motor.declare(hecho)

    motor.run()
