# ObtencionDatos
GitHub público con la práctica de Obtención de Datos, Máster Data Science - URJC.

# OBJETIVO DE LA PRÁCTICA

La práctica de la asignatura tiene como objetivo proporcionar datosen formato RDFde los transportes METRO, METRO Ligero y Cercanías RENFE,para su uso posterior en la obtención de rutas accesibles.

# RESUMENDE LA PRÁCTICA

Partiendo de la fuentede datos abiertos del Consorcio Regional de Transportesde Madrid(CRTM)[1], en formato GTFS [2], habrá que obtener los datos de las estaciones(contenidas en el fichero stops.txt) de los transportes METRO, METRO Ligero y cercanías RENFE.
Dado que en estos ficherosGTFS, las estaciones no están ordenadas según el itinerario de la línea, ni en ellos  aparece  la  línea  a  la  que  pertenece  la  estación,  será  necesario  obtener  dicho  orden  y  dicha pertenencia  a  partir  de  los  datos  de  las  líneas  de  cada  medio  de  transporte,  accesibles en  el  Consorcio Regional de Transportes de Madrid[3].

# REALIZACIÓN DE LA PRÁCTICA

El CRTM proporciona,en formato abierto, datos de los medios de transporte de la Comunidad de Madrid.Uno  de  los  formatos  que  ofrece  es  el  de  la  especificación  de  los feedsde  transporte  de Google  (GTFS). Para obtener estos ficheros GTFS, seaccederá manualmente a la página de datos abiertos del consorcio, y  se  descargarán(también  manualmente)los  ficheros  de  Metro,  Metro  Ligero  y  Cercanías,en  su correspondiente enlace GTFS, para extraer el fichero stops.txtde cada medio de transporte. 

-> Los archivos GTFS se encuentran en la carpeta GTFS_Files del github. 

Dado que estos ficheros no contienen el orden del itinerario de las líneas, ni las líneas a las que pertenece cada estación, es necesario buscar esta información realizando un scraperen [3]. Será necesario acceder al enlace  Líneasde  cada  medio  de  transporte  especificado  con  anterioridad.  Una  vez  allí,  habrá  que recorrer todas las líneas, accediendo a su contenido, con el fin deobtener la ordenación de las estaciones.

La integración de estas dos fuentes de datos se realizará en un fichero de texto en formato CSV.

Posteriormente, será necesario elaborar un diagrama conceptual con las entidades y las relaciones entre ellas,que soporte la información del dominio de este problema. Finalmente, se llevará a cabo la creación de un grafo RDF utilizando rdflib. El resultado de este último paso será un fichero RDF/XML.

# ENLACES DE INTERÉS PARA LA REALIZACIÓN DE LA PRÁCTICA
[1].Datos abiertos del Consorcio Regional de Transportede Madrid(CRTM), http://datos.crtm.es/

[2].Google Transit Feed Specification (GTFS), https://developers.google.com/transit/gtfs/reference?hl=es-419

[3].Información  de  los medios  de  transporte  en  el  CRTM, http://www.crtm.es/tu-transporte-publico.aspx
