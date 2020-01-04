import rdflib as rdf
import csv

g = Graph ()

sch = rdf.Namespace('https://schema.org')
mao = rdf.Namespace('http://com.vortic3.MANTO#')

with open('/mnt/c/Users/msalc/Qsync/docmaster/curso/programacion01/practicaObtencionDatos/scrapperMetro/scrapperMetro/stops.txt',newline='') as stopsfile:
    lineas = csv.DictReader(stopsfile, delimiter=",")
    for row in lineas: