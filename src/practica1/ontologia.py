"""
Componente Ontología y Razonamiento Semántico
"""

from rdflib import Graph, Namespace, URIRef, BNode, Literal
from rdflib.namespace import RDF, RDFS, XSD, DC, GEO
from rdflib.collection import Collection
from owlrl import DeductiveClosure, RDFS_Semantics

g = Graph()

GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
RUTA = Namespace("http://example.org/mejor_ruta#")
g.bind("ruta", RUTA)
g.bind("rdfs", RDFS)
g.bind("geo", GEO)
g.bind("rdf", RDF)
g.bind("xsd", XSD)
g.bind("dc", DC)

#Definición de Clases
g.add((RUTA.Via,RDF.type,RDFS.Class))
g.add((RUTA.Nodo,RDF.type,RDFS.Class))
g.add((RUTA.Semaforo,RDF.type,RDFS.Class))
g.add((RUTA.Evento,RDF.type,RDFS.Class))
g.add((RUTA.Ruta,RDF.type,RDFS.Class))
g.add((RUTA.Interseccion,RDF.type,RDFS.Class))
g.add((RUTA.PuntoReferencia,RDF.type,RDFS.Class))
g.add((RUTA.Calle,RDF.type,RDFS.Class))
g.add((RUTA.Avenida,RDF.type,RDFS.Class))
g.add((RUTA.Autopista,RDF.type,RDFS.Class))
g.add((RUTA.Carrera,RDF.type,RDFS.Class))
g.add((RUTA.Transversal,RDF.type,RDFS.Class))

#Jerarquía de Clases
g.add((RUTA.Interseccion,RDFS.subClassOf,RUTA.Nodo))
g.add((RUTA.PuntoReferencia,RDFS.subClassOf,RUTA.Nodo))
g.add((RUTA.Calle,RDFS.subClassOf,RUTA.Via))
g.add((RUTA.Avenida,RDFS.subClassOf,RUTA.Via))
g.add((RUTA.Autopista,RDFS.subClassOf,RUTA.Via))
g.add((RUTA.Carrera,RDFS.subClassOf,RUTA.Via))
g.add((RUTA.Transversal,RDFS.subClassOf,RUTA.Via))
g.add((RUTA.Nodo,RDFS.subClassOf,GEO.SpatialThing))
g.add((RUTA.Via,RDFS.subClassOf,GEO.SpatialThing))

#Propiedades
#Via:
g.add((RUTA.nombre,RDF.type,RDF.Property))
g.add((RUTA.nombre, RDFS.subPropertyOf, DC.title))
g.add((RUTA.nombre,RDFS.domain,RUTA.Via))
g.add((RUTA.nombre,RDFS.range,XSD.string))

g.add((RUTA.fluidez,RDF.type,RDF.Property))
g.add((RUTA.fluidez,RDFS.domain,RUTA.Via))
g.add((RUTA.fluidez,RDFS.range,XSD.string))

g.add((RUTA.tieneSemaforo,RDF.type,RDF.Property))
g.add((RUTA.tieneSemaforo,RDFS.domain,RUTA.Via))
g.add((RUTA.tieneSemaforo,RDFS.range,XSD.boolean))

g.add((RUTA.afectadaPor,RDF.type,RDF.Property))
g.add((RUTA.afectadaPor,RDFS.domain,RUTA.Via))
g.add((RUTA.afectadaPor,RDFS.range,RUTA.Evento))

g.add((RUTA.tieneVelocidadMaxima,RDF.type,RDF.Property)) #Km/H
g.add((RUTA.tieneVelocidadMaxima,RDFS.domain,RUTA.Via))
g.add((RUTA.tieneVelocidadMaxima,RDFS.range,XSD.double))

g.add((RUTA.esBidireccional,RDF.type,RDF.Property))
g.add((RUTA.esBidireccional,RDFS.domain,RUTA.Via))
g.add((RUTA.esBidireccional,RDFS.range,XSD.boolean))

#Semáforo
g.add((RUTA.tiempoEspera,RDF.type,RDF.Property))
g.add((RUTA.tiempoEspera,RDFS.domain,RUTA.Semaforo))
g.add((RUTA.tiempoEspera,RDFS.range,XSD.double))

g.add((RUTA.tieneSemaforoObj,RDF.type,RDF.Property))
g.add((RUTA.tieneSemaforoObj,RDFS.domain,RUTA.Via))
g.add((RUTA.tieneSemaforoObj,RDFS.range,RUTA.Semaforo))

g.add((RUTA.estaEnVia,RDF.type,RDF.Property))
g.add((RUTA.estaEnVia,RDFS.domain,RUTA.Semaforo))
g.add((RUTA.estaEnVia,RDFS.range,RUTA.Via))

#Ruta:
g.add((RUTA.tieneVias,RDF.type,RDF.Property))
g.add((RUTA.tieneVias,RDFS.domain,RUTA.Ruta))
#g.add((RUTA.tieneVias,RDFS.range,Collection(g, BNode())))

g.add((RUTA.tieneDistancia,RDF.type,RDF.Property))
g.add((RUTA.tieneDistancia,RDFS.domain,RUTA.Ruta))
g.add((RUTA.tieneDistancia,RDFS.range,XSD.double))

g.add((RUTA.tiempoEstimado,RDF.type,RDF.Property))
g.add((RUTA.tiempoEstimado,RDFS.domain,RUTA.Ruta))
g.add((RUTA.tiempoEstimado,RDFS.range,XSD.double))

#Evento:
g.add((RUTA.tipo,RDF.type,RDF.Property))
g.add((RUTA.tipo,RDFS.domain,RUTA.Evento))
g.add((RUTA.tipo,RDFS.range,XSD.string))

g.add((RUTA.duracion,RDF.type,RDF.Property)) #min
g.add((RUTA.duracion,RDFS.domain,RUTA.Evento))
g.add((RUTA.duracion,RDFS.range,XSD.double))

g.add((RUTA.cierreTotal,RDF.type,RDF.Property))
g.add((RUTA.cierreTotal,RDFS.domain,RUTA.Evento))
g.add((RUTA.cierreTotal,RDFS.range,XSD.boolean))

#Nodo:
g.add((RUTA.seRelacionaCon,RDF.type,RDF.Property))
g.add((RUTA.seRelacionaCon,RDFS.domain,RUTA.Nodo))
g.add((RUTA.seRelacionaCon,RDFS.range,RUTA.Nodo))

g.add((RUTA.intersectaCon,RDF.type,RDF.Property))
g.add((RUTA.intersectaCon, RDFS.subPropertyOf, RUTA.seRelacionaCon))
g.add((RUTA.intersectaCon,RDFS.domain,RUTA.Interseccion))
g.add((RUTA.intersectaCon,RDFS.range,RUTA.Interseccion))

#Conecciones entre nodos y vías
g.add((RUTA.conectaCon,RDF.type,RDF.Property))
g.add((RUTA.conectaCon,RDFS.domain,RUTA.Interseccion))
g.add((RUTA.conectaCon,RDFS.range,RUTA.Via))

g.add((RUTA.esConectada,RDF.type,RDF.Property))
g.add((RUTA.esConectada,RDFS.domain,RUTA.Via))
g.add((RUTA.esConectada,RDFS.range,RUTA.Interseccion))

#Punto de referencia:
g.add((RUTA.tieneNombre,RDF.type,RDF.Property))
g.add((RUTA.tieneNombre, RDFS.subPropertyOf, DC.title))
g.add((RUTA.tieneNombre,RDFS.domain,RUTA.PuntoReferencia))
g.add((RUTA.tieneNombre,RDFS.range,XSD.string))

#Instancias
unal=URIRef(RUTA.UNAL)
carlose=URIRef(RUTA.CARLOS_E)
exito=URIRef(RUTA.EXITO)
luisamigo=URIRef(RUTA.LUIS_AMIGO)
estadio=URIRef(RUTA.ESTADIO)
estacion=URIRef(RUTA.ESTACION)
piloto=URIRef(RUTA.PILOTO)

#Nodos referencia:
g.add((unal,RDF.type,RUTA.PuntoReferencia))
g.add((unal,RUTA.tieneNombre,Literal("Universidad Nacional de Colombia")))

g.add((carlose,RDF.type,RUTA.PuntoReferencia))
g.add((carlose,RUTA.tieneNombre,Literal("Parque Carlos E. Restrepo")))

g.add((exito,RDF.type,RUTA.PuntoReferencia))
g.add((exito,RUTA.tieneNombre,Literal("Exito Colombia")))

g.add((luisamigo,RDF.type,RUTA.PuntoReferencia))
g.add((luisamigo,RUTA.tieneNombre,Literal("Universidad Católica Luis Amigó")))

g.add((estadio,RDF.type,RUTA.PuntoReferencia))
g.add((estadio,RUTA.tieneNombre,Literal("Estadio de Fútbol Atanasio Girardot")))

g.add((estacion,RDF.type,RUTA.PuntoReferencia))
g.add((estacion,RUTA.tieneNombre,Literal("Estación Suramericana del Metro")))

g.add((piloto,RDF.type,RUTA.PuntoReferencia))
g.add((piloto,RUTA.tieneNombre,Literal("Biblioteca Pública Piloto")))

#Eventos:
g.add((RUTA.ObraVial,RDF.type,RUTA.Evento))
g.add((RUTA.ObraVial,RUTA.tipo,Literal("Obra Vial")))
g.add((RUTA.ObraVial,RUTA.duracion,Literal(360.0)))
g.add((RUTA.ObraVial,RUTA.cierreTotal,Literal(True)))

g.add((RUTA.AccidenteGrave,RDF.type,RUTA.Evento))
g.add((RUTA.AccidenteGrave,RUTA.tipo,Literal("Accidente Grave")))
g.add((RUTA.AccidenteGrave,RUTA.duracion,Literal(30.0)))
g.add((RUTA.AccidenteGrave,RUTA.cierreTotal,Literal(True)))

g.add((RUTA.ObraMenor,RDF.type,RUTA.Evento))
g.add((RUTA.ObraMenor,RUTA.tipo,Literal("Obra Menor")))
g.add((RUTA.ObraMenor,RUTA.duracion,Literal(360.0)))
g.add((RUTA.ObraMenor,RUTA.cierreTotal,Literal(False)))

g.add((RUTA.AccidenteLeve,RDF.type,RUTA.Evento))
g.add((RUTA.AccidenteLeve,RUTA.tipo,Literal("Accidente Leve")))
g.add((RUTA.AccidenteLeve,RUTA.duracion,Literal(30.0)))
g.add((RUTA.AccidenteLeve,RUTA.cierreTotal,Literal(False)))

g.add((RUTA.Manifestacion,RDF.type,RUTA.Evento))
g.add((RUTA.Manifestacion,RUTA.tipo,Literal("Manifestacion")))
g.add((RUTA.Manifestacion,RUTA.duracion,Literal(120.0)))
g.add((RUTA.Manifestacion,RUTA.cierreTotal,Literal(True)))

g.add((RUTA.VehiculoDetenido,RDF.type,RUTA.Evento))
g.add((RUTA.VehiculoDetenido,RUTA.tipo,Literal("Vehiculo Detenido")))
g.add((RUTA.VehiculoDetenido,RUTA.duracion,Literal(10.0)))
g.add((RUTA.VehiculoDetenido,RUTA.cierreTotal,Literal(False)))

g.add((RUTA.ColapsoEstructural,RDF.type,RUTA.Evento))
g.add((RUTA.ColapsoEstructural,RUTA.tipo,Literal("Colapso Estructural")))
g.add((RUTA.ColapsoEstructural,RUTA.duracion,Literal(10080.0)))
g.add((RUTA.ColapsoEstructural,RUTA.cierreTotal,Literal(True)))

#Autopista:
g.add((RUTA.AutopistaSur,RDF.type,RUTA.Autopista))
g.add((RUTA.AutopistaSur,RUTA.nombre,Literal("Autopista Sur")))
g.add((RUTA.AutopistaSur,RUTA.fluidez,Literal("Muy buena")))
g.add((RUTA.AutopistaSur,RUTA.tieneSemaforo,Literal(False)))
#g.add((RUTA.AutopistaSur,RUTA.afectadaPor,RUTA.Evento))
g.add((RUTA.AutopistaSur,RUTA.tieneVelocidadMaxima,Literal(80.0)))
g.add((RUTA.AutopistaSur,RUTA.esBidireccional,Literal(False)))

#Avenida:
g.add((RUTA.AvenidaColombia,RDF.type,RUTA.Avenida))
g.add((RUTA.AvenidaColombia,RUTA.nombre,Literal("Avenida Colombia")))
g.add((RUTA.Avenida,RUTA.fluidez,Literal("Mala")))
g.add((RUTA.AvenidaColombia,RUTA.tieneSemaforo,Literal(True)))
#g.add((RUTA.AvenidaColombia,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.AvenidaColombia,RUTA.tieneVelocidadMaxima,Literal(50.0)))
g.add((RUTA.AvenidaColombia,RUTA.esBidireccional,Literal(True)))

#Transversal:
g.add((RUTA.Transversal51a,RDF.type,RUTA.Transversal))
g.add((RUTA.Transversal51a,RUTA.nombre,Literal("Transversal 51a")))
g.add((RUTA.Transversal51a,RUTA.fluidez,Literal("Buena")))
g.add((RUTA.Transversal51a,RUTA.tieneSemaforo,Literal(True)))
#g.add((RUTA.Transversal51a,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.Transversal51a,RUTA.tieneVelocidadMaxima,Literal(30.0)))
g.add((RUTA.Transversal51a,RUTA.esBidireccional,Literal(False)))

g.add((RUTA.Transversal53A,RDF.type,RUTA.Transversal))
g.add((RUTA.Transversal53A,RUTA.nombre,Literal("Transversal 53A")))
g.add((RUTA.Transversal53A,RUTA.fluidez,Literal("Muy buena")))
g.add((RUTA.Transversal53A,RUTA.tieneSemaforo,Literal(False)))
#g.add((RUTA.Transversal53A,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.Transversal53A,RUTA.tieneVelocidadMaxima,Literal(30.0)))
g.add((RUTA.Transversal53A,RUTA.esBidireccional,Literal(False)))

g.add((RUTA.Transversal53B,RDF.type,RUTA.Transversal))
g.add((RUTA.Transversal53B,RUTA.nombre,Literal("Transversal 53B")))
g.add((RUTA.Transversal53B,RUTA.fluidez,Literal("Muy buena")))
g.add((RUTA.Transversal53B,RUTA.tieneSemaforo,Literal(False)))
#g.add((RUTA.Transversal53B,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.Transversal53B,RUTA.tieneVelocidadMaxima,Literal(30.0)))
g.add((RUTA.Transversal53B,RUTA.esBidireccional,Literal(False)))

g.add((RUTA.Diagonal63B,RDF.type,RUTA.Transversal))
g.add((RUTA.Diagonal63B,RUTA.nombre,Literal("Diagonal 63B")))
g.add((RUTA.Diagonal63B,RUTA.fluidez,Literal("Muy Buena")))
g.add((RUTA.Diagonal63B,RUTA.tieneSemaforo,Literal(False)))
#g.add((RUTA.Diagonal63B,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.Diagonal63B,RUTA.tieneVelocidadMaxima,Literal(30.0)))
g.add((RUTA.Diagonal63B,RUTA.esBidireccional,Literal(False)))

#Calle:
g.add((RUTA.Calle55,RDF.type,RUTA.Calle))
g.add((RUTA.Calle55,RUTA.nombre,Literal("Calle 55")))
g.add((RUTA.Calle55,RUTA.fluidez,Literal("Aceptable")))
g.add((RUTA.Calle55,RUTA.tieneSemaforo,Literal(True)))
#g.add((RUTA.Calle55,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.Calle55,RUTA.tieneVelocidadMaxima,Literal(30.0)))
g.add((RUTA.Calle55,RUTA.esBidireccional,Literal(True)))

g.add((RUTA.Calle48,RDF.type,RUTA.Calle))
g.add((RUTA.Calle48,RUTA.nombre,Literal("Calle 48")))
g.add((RUTA.Calle48,RUTA.fluidez,Literal("Buena")))
g.add((RUTA.Calle48,RUTA.tieneSemaforo,Literal(True)))
#g.add((RUTA.Calle48,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.Calle48,RUTA.tieneVelocidadMaxima,Literal(30.0)))
g.add((RUTA.Calle48,RUTA.esBidireccional,Literal(False)))

g.add((RUTA.Calle51,RDF.type,RUTA.Calle))
g.add((RUTA.Calle51,RUTA.nombre,Literal("Calle 51")))
g.add((RUTA.Calle51,RUTA.fluidez,Literal("Aceptable")))
g.add((RUTA.Calle51,RUTA.tieneSemaforo,Literal(True)))
#g.add((RUTA.Calle51,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.Calle51,RUTA.tieneVelocidadMaxima,Literal(30.0)))
g.add((RUTA.Calle51,RUTA.esBidireccional,Literal(False)))

g.add((RUTA.Calle48D,RDF.type,RUTA.Calle))
g.add((RUTA.Calle48D,RUTA.nombre,Literal("Calle 48D")))
g.add((RUTA.Calle48D,RUTA.fluidez,Literal("Aceptable")))
g.add((RUTA.Calle48D,RUTA.tieneSemaforo,Literal(True)))
#g.add((RUTA.Calle48D,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.Calle48D,RUTA.tieneVelocidadMaxima,Literal(30.0)))
g.add((RUTA.Calle48D,RUTA.esBidireccional,Literal(False)))

g.add((RUTA.Calle49A,RDF.type,RUTA.Calle))
g.add((RUTA.Calle49A,RUTA.nombre,Literal("Calle 49A")))
g.add((RUTA.Calle49A,RUTA.fluidez,Literal("Buena")))
g.add((RUTA.Calle49A,RUTA.tieneSemaforo,Literal(False)))
#g.add((RUTA.Calle49A,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.Calle49A,RUTA.tieneVelocidadMaxima,Literal(30.0)))
g.add((RUTA.Calle49A,RUTA.esBidireccional,Literal(False)))

g.add((RUTA.Calle49B,RDF.type,RUTA.Calle))
g.add((RUTA.Calle49B,RUTA.nombre,Literal("Calle 49B")))
g.add((RUTA.Calle49,RUTA.fluidez,Literal("Buena")))
g.add((RUTA.Calle49B,RUTA.tieneSemaforo,Literal(True)))
#g.add((RUTA.Calle49B,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.Calle49B,RUTA.tieneVelocidadMaxima,Literal(30.0)))
g.add((RUTA.Calle49B,RUTA.esBidireccional,Literal(False)))

g.add((RUTA.Calle53,RDF.type,RUTA.Calle))
g.add((RUTA.Calle53,RUTA.nombre,Literal("Calle 53")))
g.add((RUTA.Calle53,RUTA.fluidez,Literal("Aceptable")))
g.add((RUTA.Calle53,RUTA.tieneSemaforo,Literal(True)))
#g.add((RUTA.Calle53,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.Calle53,RUTA.tieneVelocidadMaxima,Literal(30.0)))
g.add((RUTA.Calle53,RUTA.esBidireccional,Literal(False)))

g.add((RUTA.Calle52,RDF.type,RUTA.Calle))
g.add((RUTA.Calle52,RUTA.nombre,Literal("Calle 52")))
g.add((RUTA.Calle52,RUTA.fluidez,Literal("Buena")))
g.add((RUTA.Calle52,RUTA.tieneSemaforo,Literal(False)))
#g.add((RUTA.Calle52,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.Calle52,RUTA.tieneVelocidadMaxima,Literal(30.0)))
g.add((RUTA.Calle52,RUTA.esBidireccional,Literal(False)))

#Carrera
g.add((RUTA.Carrera65,RDF.type,RUTA.Carrera))
g.add((RUTA.Carrera65,RUTA.nombre,Literal("Carrera 65")))
g.add((RUTA.Carrera65,RUTA.fluidez,Literal("Aceptable")))
g.add((RUTA.Carrera65,RUTA.tieneSemaforo,Literal(True)))
#g.add((RUTA.Carrera65,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.Carrera65,RUTA.tieneVelocidadMaxima,Literal(30.0)))
g.add((RUTA.Carrera65,RUTA.esBidireccional,Literal(True)))

g.add((RUTA.Carrera66,RDF.type,RUTA.Carrera))
g.add((RUTA.Carrera66,RUTA.nombre,Literal("Carrera 66")))
g.add((RUTA.Carrera66,RUTA.fluidez,Literal("Aceptable")))
g.add((RUTA.Carrera66,RUTA.tieneSemaforo,Literal(True)))
#g.add((RUTA.Carrera66,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.Carrera66,RUTA.tieneVelocidadMaxima,Literal(30.0)))
g.add((RUTA.Carrera66,RUTA.esBidireccional,Literal(False)))

g.add((RUTA.Carrera67,RDF.type,RUTA.Carrera))
g.add((RUTA.Carrera67,RUTA.nombre,Literal("Carrera 67")))
g.add((RUTA.Carrera67,RUTA.fluidez,Literal("Aceptable")))
g.add((RUTA.Carrera67,RUTA.tieneSemaforo,Literal(True)))
#g.add((RUTA.Carrera67,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.Carrera67,RUTA.tieneVelocidadMaxima,Literal(30.0)))
g.add((RUTA.Carrera67,RUTA.esBidireccional,Literal(False)))

g.add((RUTA.Carrera73,RDF.type,RUTA.Carrera))
g.add((RUTA.Carrera73,RUTA.nombre,Literal("Carrera 73")))
g.add((RUTA.Carrera73,RUTA.fluidez,Literal("Muy buena")))
g.add((RUTA.Carrera73,RUTA.tieneSemaforo,Literal(True)))
#g.add((RUTA.Carrera73,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.Carrera73,RUTA.tieneVelocidadMaxima,Literal(30.0)))
g.add((RUTA.Carrera73,RUTA.esBidireccional,Literal(False)))

g.add((RUTA.Carrera74,RDF.type,RUTA.Carrera))
g.add((RUTA.Carrera74,RUTA.nombre,Literal("Carrera 74")))
g.add((RUTA.Carrera74,RUTA.fluidez,Literal("Mala")))
g.add((RUTA.Carrera74,RUTA.tieneSemaforo,Literal(True)))
#g.add((RUTA.Carrera74,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.Carrera74,RUTA.tieneVelocidadMaxima,Literal(30.0)))
g.add((RUTA.Carrera74,RUTA.esBidireccional,Literal(True)))

g.add((RUTA.Carrera67B,RDF.type,RUTA.Carrera))
g.add((RUTA.Carrera67B,RUTA.nombre,Literal("Carrera 67B")))
g.add((RUTA.Carrera67B,RUTA.fluidez,Literal("Mala")))
g.add((RUTA.Carrera67B,RUTA.tieneSemaforo,Literal(False)))
#g.add((RUTA.Carrera67B,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.Carrera67B,RUTA.tieneVelocidadMaxima,Literal(30.0)))
g.add((RUTA.Carrera67B,RUTA.esBidireccional,Literal(False)))

g.add((RUTA.BulevarLibertadores,RDF.type,RUTA.Carrera))
g.add((RUTA.BulevarLibertadores,RUTA.nombre,Literal("Bulevar Libertadores de América")))
g.add((RUTA.BulevarLibertadores,RUTA.fluidez,Literal("Muy mala")))
g.add((RUTA.BulevarLibertadores,RUTA.tieneSemaforo,Literal(True)))
#g.add((RUTA.BulevarLibertadores,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.BulevarLibertadores,RUTA.tieneVelocidadMaxima,Literal(30.0)))
g.add((RUTA.BulevarLibertadores,RUTA.esBidireccional,Literal(False)))

g.add((RUTA.Carrera68,RDF.type,RUTA.Carrera))
g.add((RUTA.Carrera68,RUTA.nombre,Literal("Carrera 68")))
g.add((RUTA.Carrera68,RUTA.fluidez,Literal("Buena")))
g.add((RUTA.Carrera68,RUTA.tieneSemaforo,Literal(True)))
#g.add((RUTA.Carrera68,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.Carrera68,RUTA.tieneVelocidadMaxima,Literal(30.0)))
g.add((RUTA.Carrera68,RUTA.esBidireccional,Literal(False)))

g.add((RUTA.Carrera64,RDF.type,RUTA.Carrera))
g.add((RUTA.Carrera64,RUTA.nombre,Literal("Carrera 64")))
g.add((RUTA.Carrera64,RUTA.fluidez,Literal("Buena")))
g.add((RUTA.Carrera64,RUTA.tieneSemaforo,Literal(True)))
#g.add((RUTA.Carrera64,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.Carrera64,RUTA.tieneVelocidadMaxima,Literal(30.0)))
g.add((RUTA.Carrera64,RUTA.esBidireccional,Literal(False)))

g.add((RUTA.Carrera64B,RDF.type,RUTA.Carrera))
g.add((RUTA.Carrera64B,RUTA.nombre,Literal("Carrera 64B")))
g.add((RUTA.Carrera64B,RUTA.fluidez,Literal("Muy Buena")))
g.add((RUTA.Carrera64B,RUTA.tieneSemaforo,Literal(True)))
#g.add((RUTA.Carrera64B,RUTA.afectadaPor,RUTA.ObraVial))
g.add((RUTA.Carrera64B,RUTA.tieneVelocidadMaxima,Literal(30.0)))
g.add((RUTA.Carrera64B,RUTA.esBidireccional,Literal(False)))

#Intersecciones:
intersecciones = {f"Interseccion{i}": BNode() for i in range(1, 52)}

for nombre, nodo in intersecciones.items():
    g.add((nodo, RDF.type, RUTA.Interseccion))

def intersecta(nodo1, nodo2, via):
    g.add((nodo1, RUTA.intersectaCon, nodo2))
    g.add((nodo1, RUTA.conectaCon, via))
    g.add((via, RUTA.esConectada, nodo2))

intersecta(intersecciones["Interseccion1"], intersecciones["Interseccion3"],RUTA.Calle55)
intersecta(intersecciones["Interseccion2"], intersecciones["Interseccion3"],RUTA.BulevarLibertadores)
intersecta(intersecciones["Interseccion3"], intersecciones["Interseccion4"],RUTA.Calle55)
intersecta(intersecciones["Interseccion3"], intersecciones["Interseccion21"],RUTA.BulevarLibertadores)
intersecta(intersecciones["Interseccion4"], intersecciones["Interseccion2"],RUTA.Calle55)
intersecta(intersecciones["Interseccion4"], intersecciones["Interseccion19"],RUTA.Calle55)
intersecta(intersecciones["Interseccion5"], intersecciones["Interseccion17"],RUTA.Carrera65)
intersecta(intersecciones["Interseccion6"], intersecciones["Interseccion7"],RUTA.Calle55)
intersecta(intersecciones["Interseccion7"], intersecciones["Interseccion13"],RUTA.Calle55)
intersecta(intersecciones["Interseccion7"], intersecciones["Interseccion8"],RUTA.AutopistaSur)
intersecta(intersecciones["Interseccion8"], intersecciones["Interseccion9"],RUTA.AutopistaSur)
intersecta(intersecciones["Interseccion9"], intersecciones["Interseccion10"],RUTA.AutopistaSur)
intersecta(intersecciones["Interseccion10"], intersecciones["Interseccion37"],RUTA.AvenidaColombia)
intersecta(intersecciones["Interseccion10"], intersecciones["Interseccion11"],RUTA.AutopistaSur)
intersecta(intersecciones["Interseccion11"], intersecciones["Interseccion31"],RUTA.AutopistaSur)
intersecta(intersecciones["Interseccion12"], intersecciones["Interseccion9"],RUTA.Calle52)
intersecta(intersecciones["Interseccion13"], intersecciones["Interseccion7"],RUTA.Calle55)
intersecta(intersecciones["Interseccion7"], intersecciones["Interseccion6"],RUTA.Calle55)
intersecta(intersecciones["Interseccion12"], intersecciones["Interseccion36"],RUTA.Carrera64)
intersecta(intersecciones["Interseccion13"], intersecciones["Interseccion8"],RUTA.Diagonal63B)
intersecta(intersecciones["Interseccion14"], intersecciones["Interseccion13"],RUTA.Calle55)
intersecta(intersecciones["Interseccion14"], intersecciones["Interseccion15"],RUTA.Carrera64)
intersecta(intersecciones["Interseccion14"], intersecciones["Interseccion17"],RUTA.Calle55)
intersecta(intersecciones["Interseccion15"], intersecciones["Interseccion12"],RUTA.Carrera64)
intersecta(intersecciones["Interseccion16"], intersecciones["Interseccion15"],RUTA.Calle53)
intersecta(intersecciones["Interseccion17"], intersecciones["Interseccion19"],RUTA.Calle55)
intersecta(intersecciones["Interseccion17"], intersecciones["Interseccion14"],RUTA.Calle55)
intersecta(intersecciones["Interseccion17"], intersecciones["Interseccion18"],RUTA.Carrera65)
intersecta(intersecciones["Interseccion18"], intersecciones["Interseccion16"],RUTA.Transversal53A)
intersecta(intersecciones["Interseccion18"], intersecciones["Interseccion40"],RUTA.Carrera65)
intersecta(intersecciones["Interseccion19"], intersecciones["Interseccion17"],RUTA.Calle55)
intersecta(intersecciones["Interseccion19"], intersecciones["Interseccion18"],RUTA.Transversal53B)
intersecta(intersecciones["Interseccion20"], intersecciones["Interseccion21"],RUTA.Transversal51a)
intersecta(intersecciones["Interseccion19"], intersecciones["Interseccion4"],RUTA.Calle55)
intersecta(intersecciones["Interseccion20"], intersecciones["Interseccion4"],RUTA.Carrera67B)
intersecta(intersecciones["Interseccion20"], intersecciones["Interseccion49"],RUTA.Calle51)
intersecta(intersecciones["Interseccion21"], intersecciones["Interseccion49"],RUTA.BulevarLibertadores)
intersecta(intersecciones["Interseccion22"], intersecciones["Interseccion1"],RUTA.Carrera73)
intersecta(intersecciones["Interseccion23"], intersecciones["Interseccion22"],RUTA.Carrera73)
intersecta(intersecciones["Interseccion23"], intersecciones["Interseccion24"],RUTA.AvenidaColombia)
intersecta(intersecciones["Interseccion23"], intersecciones["Interseccion50"],RUTA.AvenidaColombia)
intersecta(intersecciones["Interseccion24"], intersecciones["Interseccion23"],RUTA.AvenidaColombia)
intersecta(intersecciones["Interseccion24"], intersecciones["Interseccion25"],RUTA.Carrera74)
intersecta(intersecciones["Interseccion25"], intersecciones["Interseccion24"],RUTA.Carrera74)
intersecta(intersecciones["Interseccion25"], intersecciones["Interseccion26"],RUTA.Calle48)
intersecta(intersecciones["Interseccion26"], intersecciones["Interseccion25"],RUTA.Calle48)
intersecta(intersecciones["Interseccion26"], intersecciones["Interseccion27"],RUTA.Calle48)
intersecta(intersecciones["Interseccion27"], intersecciones["Interseccion48"],RUTA.Carrera68)
intersecta(intersecciones["Interseccion27"], intersecciones["Interseccion28"],RUTA.Calle48)
intersecta(intersecciones["Interseccion27"], intersecciones["Interseccion26"],RUTA.Calle48)
intersecta(intersecciones["Interseccion28"], intersecciones["Interseccion27"],RUTA.Calle48)
intersecta(intersecciones["Interseccion28"], intersecciones["Interseccion29"],RUTA.Calle48)
intersecta(intersecciones["Interseccion29"], intersecciones["Interseccion28"],RUTA.Calle48)
intersecta(intersecciones["Interseccion29"], intersecciones["Interseccion30"],RUTA.Calle48)
intersecta(intersecciones["Interseccion29"], intersecciones["Interseccion43"],RUTA.Carrera66)
intersecta(intersecciones["Interseccion30"], intersecciones["Interseccion29"],RUTA.Calle48)
intersecta(intersecciones["Interseccion30"], intersecciones["Interseccion31"],RUTA.Calle48)
intersecta(intersecciones["Interseccion30"], intersecciones["Interseccion38"],RUTA.Carrera65)
intersecta(intersecciones["Interseccion31"], intersecciones["Interseccion30"],RUTA.Calle48)
intersecta(intersecciones["Interseccion32"], intersecciones["Interseccion11"],RUTA.Calle49A)
intersecta(intersecciones["Interseccion33"], intersecciones["Interseccion32"],RUTA.Carrera64B)
intersecta(intersecciones["Interseccion34"], intersecciones["Interseccion33"],RUTA.Carrera64B)
intersecta(intersecciones["Interseccion38"], intersecciones["Interseccion39"],RUTA.Carrera65)
intersecta(intersecciones["Interseccion39"], intersecciones["Interseccion40"],RUTA.Carrera65)
intersecta(intersecciones["Interseccion40"], intersecciones["Interseccion18"],RUTA.Carrera65)
intersecta(intersecciones["Interseccion18"], intersecciones["Interseccion17"],RUTA.Carrera65)
intersecta(intersecciones["Interseccion17"], intersecciones["Interseccion5"],RUTA.Carrera65)
intersecta(intersecciones["Interseccion34"], intersecciones["Interseccion37"],RUTA.AvenidaColombia)
intersecta(intersecciones["Interseccion34"], intersecciones["Interseccion39"],RUTA.AvenidaColombia)
intersecta(intersecciones["Interseccion35"], intersecciones["Interseccion16"],RUTA.Calle53)
intersecta(intersecciones["Interseccion35"], intersecciones["Interseccion40"],RUTA.Calle51)
intersecta(intersecciones["Interseccion35"], intersecciones["Interseccion34"],RUTA.Carrera64B)
intersecta(intersecciones["Interseccion36"], intersecciones["Interseccion35"],RUTA.Calle51)
intersecta(intersecciones["Interseccion36"], intersecciones["Interseccion37"],RUTA.Carrera64)
intersecta(intersecciones["Interseccion37"], intersecciones["Interseccion34"],RUTA.AvenidaColombia)
intersecta(intersecciones["Interseccion37"], intersecciones["Interseccion11"],RUTA.AvenidaColombia)
intersecta(intersecciones["Interseccion9"], intersecciones["Interseccion37"],RUTA.AvenidaColombia)
intersecta(intersecciones["Interseccion37"], intersecciones["Interseccion10"],RUTA.AvenidaColombia)
intersecta(intersecciones["Interseccion38"], intersecciones["Interseccion30"],RUTA.Carrera65)
intersecta(intersecciones["Interseccion38"], intersecciones["Interseccion33"],RUTA.Calle49B)
intersecta(intersecciones["Interseccion39"], intersecciones["Interseccion38"],RUTA.Carrera65)
intersecta(intersecciones["Interseccion39"], intersecciones["Interseccion41"],RUTA.AvenidaColombia)
intersecta(intersecciones["Interseccion39"], intersecciones["Interseccion34"],RUTA.AvenidaColombia)
intersecta(intersecciones["Interseccion40"], intersecciones["Interseccion39"],RUTA.Carrera65)
intersecta(intersecciones["Interseccion40"], intersecciones["Interseccion20"],RUTA.Calle51)
intersecta(intersecciones["Interseccion41"], intersecciones["Interseccion44"],RUTA.AvenidaColombia)
intersecta(intersecciones["Interseccion41"], intersecciones["Interseccion39"],RUTA.AvenidaColombia)
intersecta(intersecciones["Interseccion42"], intersecciones["Interseccion41"],RUTA.Carrera66)
intersecta(intersecciones["Interseccion42"], intersecciones["Interseccion38"],RUTA.Calle49B)
intersecta(intersecciones["Interseccion43"], intersecciones["Interseccion42"],RUTA.Carrera66)
intersecta(intersecciones["Interseccion44"], intersecciones["Interseccion20"],RUTA.Transversal51a)
intersecta(intersecciones["Interseccion44"], intersecciones["Interseccion41"],RUTA.AvenidaColombia)
intersecta(intersecciones["Interseccion44"], intersecciones["Interseccion50"],RUTA.AvenidaColombia)
intersecta(intersecciones["Interseccion44"], intersecciones["Interseccion45"],RUTA.Carrera67)
intersecta(intersecciones["Interseccion45"], intersecciones["Interseccion42"],RUTA.Calle49B)
intersecta(intersecciones["Interseccion45"], intersecciones["Interseccion46"],RUTA.Carrera67)
intersecta(intersecciones["Interseccion46"], intersecciones["Interseccion28"],RUTA.Carrera67)
intersecta(intersecciones["Interseccion46"], intersecciones["Interseccion43"],RUTA.Calle48D)
intersecta(intersecciones["Interseccion47"], intersecciones["Interseccion45"],RUTA.Calle49B)
intersecta(intersecciones["Interseccion48"], intersecciones["Interseccion47"],RUTA.Carrera68)
intersecta(intersecciones["Interseccion48"], intersecciones["Interseccion46"],RUTA.Calle48D)
intersecta(intersecciones["Interseccion49"], intersecciones["Interseccion22"],RUTA.Calle51)
intersecta(intersecciones["Interseccion49"], intersecciones["Interseccion50"],RUTA.BulevarLibertadores)
intersecta(intersecciones["Interseccion50"], intersecciones["Interseccion51"],RUTA.BulevarLibertadores)
intersecta(intersecciones["Interseccion50"], intersecciones["Interseccion23"],RUTA.AvenidaColombia)
intersecta(intersecciones["Interseccion50"], intersecciones["Interseccion44"],RUTA.AvenidaColombia)
intersecta(intersecciones["Interseccion51"], intersecciones["Interseccion26"],RUTA.BulevarLibertadores)
intersecta(intersecciones["Interseccion51"], intersecciones["Interseccion47"],RUTA.Calle49B)

#Intersecciones accesibles desde Puntos de referencia
g.add((estadio,RUTA.conectaCon,intersecciones["Interseccion25"]))
g.add((estacion,RUTA.conectaCon,intersecciones["Interseccion30"]))
g.add((exito,RUTA.conectaCon,intersecciones["Interseccion41"]))
g.add((luisamigo,RUTA.conectaCon,intersecciones["Interseccion20"]))
g.add((carlose,RUTA.conectaCon,intersecciones["Interseccion36"]))
g.add((piloto,RUTA.conectaCon,intersecciones["Interseccion9"]))
g.add((unal,RUTA.conectaCon,intersecciones["Interseccion5"]))
g.add((unal,RUTA.conectaCon,intersecciones["Interseccion6"]))

#Agregar semáforos a las vías
def agregar_semaforo(via, tiempo):
    semaforo = BNode()
    g.add((semaforo, RDF.type, RUTA.Semaforo))
    g.add((semaforo, RUTA.tiempoEspera, Literal(tiempo, datatype=XSD.double)))
    g.add((semaforo, RUTA.estaEnVia, via))
    g.add((via, RUTA.tieneSemaforoObj, semaforo))
    return semaforo

agregar_semaforo(RUTA.AvenidaColombia, 45.0)
agregar_semaforo(RUTA.Transversal51A, 40.0)
agregar_semaforo(RUTA.Calle55, 35.0)
agregar_semaforo(RUTA.Calle48, 30.0)
agregar_semaforo(RUTA.Calle51, 50.0)
agregar_semaforo(RUTA.Calle48D, 30.0)
agregar_semaforo(RUTA.Calle49B, 40.0)
agregar_semaforo(RUTA.Calle53, 35.0)
agregar_semaforo(RUTA.Carrera65, 60.0)
agregar_semaforo(RUTA.Carrera66, 45.0)
agregar_semaforo(RUTA.Carrera67, 40.0)
agregar_semaforo(RUTA.Carrera73, 55.0)
agregar_semaforo(RUTA.Carrera74, 50.0)
agregar_semaforo(RUTA.BulevarLibertadoresDeAmerica, 45.0)
agregar_semaforo(RUTA.Carrera68, 35.0)
agregar_semaforo(RUTA.Carrera64, 40.0)
agregar_semaforo(RUTA.Carrera64B, 30.0)

print('Tripletas elaboradas a mano:',len(g),'\n')

#Método para crear rutas
def crear_ruta(vias, distancia, tiempo):
    ruta = BNode()
    g.add((ruta, RDF.type, RUTA.Ruta))
    g.add((ruta, RUTA.tieneDistancia, Literal(distancia, datatype=XSD.double)))
    g.add((ruta, RUTA.tiempoEstimado, Literal(tiempo, datatype=XSD.double)))

    lista_vias = BNode()
    Collection(g, lista_vias, vias)
    g.add((ruta, RUTA.tieneVias, lista_vias))
    
    return ruta

ruta1 = crear_ruta(
    [RUTA.Carrera65, RUTA.Calle53, RUTA.Carrera73],
    distancia=2.5, 
    tiempo=8.0
)

#Razonador

#Guardamos las tripletas antes del razonamiento
g1=set(g)

print(f"Antes del análisis existe {len(g1)} tripletas\n")

'''print("=== Tripletas de tipos antes del razonamiento ===")
for s, p, o in g:
    if p == RDF.type:
        print(f"{s} {p} {o}")


print("=== Tripletas de propiedades antes del razonamiento ===")
for s, p, o in g:
    if (str(s).startswith(str(RUTA)) or str(o).startswith(str(RUTA))) and (o!=RDFS.Resource) and (p!=RDFS.subClassOf) and (p!=RDFS.subPropertyOf):
        print(f"{s} {p} {o}")

print("=== Tripletas totales antes del razonamiento ===")
for s, p, o in g:
    print(f"{s} {p} {o}")'''

# Aplicamos razonamiento de la librería owlrl
DeductiveClosure(RDFS_Semantics, axiomatic_triples=True, datatype_axioms=False).expand(g)

print(f"Tras el análisis existen {len(g)} tripletas.\n")

#Guardamos las tripletas después del razonamiento
g2=set(g)

print(f"Se han generado {len(g2-g1)} nuevas tripletas.\n")

# Ver resultados

'''print("=== Tripletas de tipos después del razonamiento ===")
for s, p, o in g:
    if p == RDF.type:
        print(f"{s} {p} {o}")


print("=== Tripletas de propiedades después del razonamiento ===")
for s, p, o in g:
    if (str(s).startswith(str(RUTA)) or str(o).startswith(str(RUTA))) and (o!=RDFS.Resource) and (p!=RDFS.subClassOf) and (p!=RDFS.subPropertyOf):
        print(f"{s} {p} {o}")

print("=== Tripletas totales después del razonamiento ===")
for s, p, o in g:
    print(f"{s} {p} {o}")'''


#Serialización final
#print(g.serialize(format="turtle"))
