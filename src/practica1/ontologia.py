"""
Componente Ontología y Razonamiento Semántico
"""

from rdflib import RDF, RDFS, Graph, Literal, Namespace
import owlrl

g = Graph()

ex = Namespace("http://example.org/")
g.bind("ex", ex)

g.add((ex.Libro, RDF.type, RDFS.Class))

g.add((ex.ElSeñorDeLosAnillos, RDF.type, ex.Libro))
g.add((ex.ElSeñorDeLosAnillos, ex.titulo, Literal("El Señor De Los Anillos")))
g.add((ex.ElSeñorDeLosAnillos, ex.titulo, Literal("Otra cosa")))

owlrl.DeductiveClosure(owlrl.RDFS_Semantics).expand(g)
