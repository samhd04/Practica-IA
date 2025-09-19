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

    # traducción del grafo de ontologias a hechos del sistema experto
    hechos = traducir(g)

    print("Traducción completada")

    print("\nHechos traducidos:", *map(repr, hechos), sep="\n\t")

    # declaramos los hechos en el motor
    motor.declare(*hechos)

    motor.run()

if __name__ == "__main__":
    main()
