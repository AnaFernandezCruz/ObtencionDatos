import rdflib as rdf
import csv
import unicodedata

g = rdf.Graph ()

prefijoUris = 'http://www.meinventoesto.com/'

sch = rdf.Namespace('https://schema.org')
manto = rdf.Namespace('http://com.vortic3.MANTO#')
rdfSch = rdf.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
uriLocal = rdf.Namespace('http://www.meinventoesto.com/')
rdfsSch = rdf.Namespace('http://www.w3.org/2000/01/rdf-schema#')
geoSch = rdf.Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')

# esta variable controla el tipo de exportacion en rdf
# si es 0 la relacion entre estacion siguiente/anterior no tendra como atributo la linea a la que pertenece esa relacion
# si es 1 la relacion si que tendra la linea
tipoExportacionEnlaces = 0

mediosTransporte = {'METRO' : prefijoUris+'medioTransporte'+'#metro', 'CR':prefijoUris+'medioTransporte'+'#cercanias','ML':prefijoUris+'medioTransporte'+'#metroLigero'}
uriTipoMedioTransporte = uriLocal.tipoMedioTransporte  #rdf.URIRef(prefijoUris+'tipoMedioTransporte')
uriTipoLinea =  uriLocal.linea #rdf.URIRef(prefijoUris+'linea')
uriTipoEstacion = uriLocal.estacion #rdf.URIRef(prefijoUris+'estacion')
uriTipoEnlaceSiguiente = uriLocal.enlaceSiguiente #rdf.URIRef(prefijoUris+'enlaceSiguiente')
uriTipoEnlaceAnterior = uriLocal.enlaceAnterior  #rdf.URIRef(prefijoUris+'enlaceAnterior')
uriEstacionEnlace = uriLocal.estacionEnlace
uriMedioTransporteAsociado = uriLocal.medioTransporteAsociado #rdf.URIRef(prefijoUris+'medioTransporteAsociado')
uriLineaEnlace = uriLocal.lineaEnlace
uriTieneRampa =  manto.hasRamp
uriStopId =  uriLocal.stopId
uriStopCode =  uriLocal.stopCode
uriStopDesc =  uriLocal.stopDesc
uriZoneId =  uriLocal.zoneId
uriLocationType =  uriLocal.locationType
uriStopTimeZone =  uriLocal.stopTimeZone
uriEstacionPerteneceLinea = manto.ofLine
uriLat = geoSch.lat
uriLon = geoSch.lon


for medioTransporte in mediosTransporte.keys():
    uriMedioTransporte = rdf.URIRef(mediosTransporte[medioTransporte])
    g.add ( (uriMedioTransporte, rdfSch.type, uriTipoMedioTransporte) )
    g.add ( (uriMedioTransporte, rdfsSch.label, rdf.Literal(medioTransporte)) )

lineasFicheroIndexadasClave = {}
estacionesIndexadas = {}
lineasIndexadas = {}
enlacesIndexados = {}
lineaAnterior = None
tipoMedioTransporteAnterior = None
secuencialIdentificadorEnlaces  = 0

#funcion para obtener los literales sin acentos 
def strip_accents_spain(string, accents=('COMBINING ACUTE ACCENT', 'COMBINING GRAVE ACCENT')):
    accents = set(map(unicodedata.lookup, accents))
    chars = [c for c in unicodedata.normalize('NFD', string) if c not in accents]
    return unicodedata.normalize('NFC', ''.join(chars)).replace(" ", "_")


def generaUriLinea(tipoMedioTransporte,nombreLinea):
    return rdf.URIRef(prefijoUris+'lineas/'+tipoMedioTransporte.lower()+'/'+nombreLinea.lower())

def generaUriMedioTransporte(tipoMedioTransporte):
    return rdf.URIRef(mediosTransporte[tipoMedioTransporte])

def generaUriEstacionMetro(tipoMedioTransporte,nombreLinea,nombreEstacion,idEstacion):
    return rdf.URIRef(prefijoUris+'estaciones/'+tipoMedioTransporte.lower()+'/'+idEstacion+'/'+strip_accents_spain(nombreEstacion.lower()))

def generaUriEnlace():
    global secuencialIdentificadorEnlaces
    secuencialIdentificadorEnlaces=secuencialIdentificadorEnlaces+1
    return rdf.URIRef(prefijoUris+'enlaces/'+str(secuencialIdentificadorEnlaces))
    

def insertarNuevaLinea(gr,tipoMedioTransporte,nombreLinea):
    if not tipoMedioTransporte.lower()+'_'+nombreLinea.lower() in lineasIndexadas.keys():
        uriLinea= generaUriLinea(tipoMedioTransporte,nombreLinea)
        uriMedioTransporte = generaUriMedioTransporte(tipoMedioTransporte)
        gr.add ( (uriLinea, rdfSch.type, uriTipoLinea) )
        gr.add ( (uriLinea, rdfsSch.label, rdf.Literal(' linea de '+tipoMedioTransporte.lower()+' '+nombreLinea.lower())) )
        gr.add ( (uriLinea,uriMedioTransporteAsociado, uriMedioTransporte) )
        lineasIndexadas[tipoMedioTransporte.lower()+'_'+nombreLinea.lower()] = uriLinea


def insertarEnlacePrevioSimplificado(gr,filaDatosEstacionActual,filaDatosEstacionAnterior):
    if not filaDatosEstacionAnterior['stop_id']+'_'+filaDatosEstacionActual['stop_id']+'_'+filaDatosEstacionActual['line_number']+'_s' in enlacesIndexados.keys():
        if filaDatosEstacionActual['line_number'] == filaDatosEstacionAnterior['line_number'] and filaDatosEstacionActual['transportmean_name'] == filaDatosEstacionAnterior['transportmean_name']:
            gr.add ( ( generaUriEstacionMetro(filaDatosEstacionActual['transportmean_name'],filaDatosEstacionActual['line_number'],filaDatosEstacionActual['stop_name'],filaDatosEstacionActual['stop_id']) , uriTipoEnlaceAnterior, generaUriEstacionMetro(filaDatosEstacionAnterior['transportmean_name'],filaDatosEstacionAnterior['line_number'],filaDatosEstacionAnterior['stop_name'],filaDatosEstacionAnterior['stop_id'])) )
            enlacesIndexados[filaDatosEstacionAnterior['stop_id']+'_'+filaDatosEstacionActual['stop_id']+'_'+filaDatosEstacionActual['line_number']+'_s'] = '1'



#el enlace se crea unicamente cuando tanto la estacion actual como la anterior pertenecen a la misma linea y al mismo medio de tranporte
def insertarEnlacePrevio(gr,filaDatosEstacionActual,filaDatosEstacionAnterior):
    if not filaDatosEstacionAnterior['stop_id']+'_'+filaDatosEstacionActual['stop_id']+'_'+filaDatosEstacionActual['line_number']+'_a' in enlacesIndexados.keys():
        if filaDatosEstacionActual['line_number'] == filaDatosEstacionAnterior['line_number'] and filaDatosEstacionActual['transportmean_name'] == filaDatosEstacionAnterior['transportmean_name']:
            uriEnlace = generaUriEnlace()
            gr.add ( (uriEnlace, rdfSch.type, uriTipoEnlaceAnterior) )
            gr.add ( (uriEnlace, uriLineaEnlace, generaUriLinea(filaDatosEstacionActual['transportmean_name'],filaDatosEstacionAnterior['line_number'])) )
            gr.add ( (uriEnlace, uriEstacionEnlace, generaUriEstacionMetro(filaDatosEstacionAnterior['transportmean_name'],filaDatosEstacionAnterior['line_number'],filaDatosEstacionAnterior['stop_name'],filaDatosEstacionAnterior['stop_id'])) )
            gr.add ( ( generaUriEstacionMetro(filaDatosEstacionActual['transportmean_name'],filaDatosEstacionActual['line_number'],filaDatosEstacionActual['stop_name'],filaDatosEstacionActual['stop_id']) , uriTipoEnlaceAnterior, uriEnlace) )
            enlacesIndexados[filaDatosEstacionAnterior['stop_id']+'_'+filaDatosEstacionActual['stop_id']+'_'+filaDatosEstacionActual['line_number']+'_a'] = uriEnlace
    #else:
    #    if filaDatosEstacionActual['line_number'] == filaDatosEstacionAnterior['line_number'] and filaDatosEstacionActual['transportmean_name'] == filaDatosEstacionAnterior['transportmean_name']:
    #        gr.add ( ( generaUriEstacionMetro(filaDatosEstacionActual['transportmean_name'],filaDatosEstacionActual['line_number'],filaDatosEstacionActual['stop_name'],filaDatosEstacionActual['stop_id']) , uriTipoEnlaceAnterior, enlacesIndexados[filaDatosEstacionAnterior['stop_id']+'_'+filaDatosEstacionActual['stop_id']+'_'+filaDatosEstacionActual['line_number']]) )


def insertarEnlaceSiguienteSimplificado(gr,filaDatosEstacionActual,filaDatosEstacionSiguiente):
    if not filaDatosEstacionActual['stop_id']+'_'+filaDatosEstacionSiguiente['stop_id']+'_'+filaDatosEstacionSiguiente['line_number'] in enlacesIndexados.keys():
        if filaDatosEstacionActual['line_number'] == filaDatosEstacionSiguiente['line_number'] and filaDatosEstacionActual['transportmean_name'] == filaDatosEstacionSiguiente['transportmean_name']:
            gr.add ( ( generaUriEstacionMetro(filaDatosEstacionActual['transportmean_name'],filaDatosEstacionActual['line_number'],filaDatosEstacionActual['stop_name'],filaDatosEstacionActual['stop_id']) , uriTipoEnlaceSiguiente, generaUriEstacionMetro(filaDatosEstacionSiguiente['transportmean_name'],filaDatosEstacionSiguiente['line_number'],filaDatosEstacionSiguiente['stop_name'],filaDatosEstacionSiguiente['stop_id'])) )
            enlacesIndexados[filaDatosEstacionActual['stop_id']+'_'+filaDatosEstacionSiguiente['stop_id']+'_'+filaDatosEstacionSiguiente['line_number']] = '1'


def insertarEnlaceSiguiente(gr,filaDatosEstacionActual,filaDatosEstacionSiguiente):
    if not filaDatosEstacionActual['stop_id']+'_'+filaDatosEstacionSiguiente['stop_id']+'_'+filaDatosEstacionSiguiente['line_number']+'_s' in enlacesIndexados.keys():
        if filaDatosEstacionActual['line_number'] == filaDatosEstacionSiguiente['line_number'] and filaDatosEstacionActual['transportmean_name'] == filaDatosEstacionSiguiente['transportmean_name']:
            uriEnlace = generaUriEnlace()
            gr.add ( (uriEnlace, rdfSch.type, uriTipoEnlaceSiguiente) )
            gr.add ( (uriEnlace, uriLineaEnlace, generaUriLinea(filaDatosEstacionActual['transportmean_name'],filaDatosEstacionSiguiente['line_number'])) )
            gr.add ( (uriEnlace, uriEstacionEnlace, generaUriEstacionMetro(filaDatosEstacionSiguiente['transportmean_name'],filaDatosEstacionSiguiente['line_number'],filaDatosEstacionSiguiente['stop_name'],filaDatosEstacionSiguiente['stop_id'])) )
            gr.add ( ( generaUriEstacionMetro(filaDatosEstacionActual['transportmean_name'],filaDatosEstacionActual['line_number'],filaDatosEstacionActual['stop_name'],filaDatosEstacionActual['stop_id']) , uriTipoEnlaceSiguiente, uriEnlace) )
            enlacesIndexados[filaDatosEstacionActual['stop_id']+'_'+filaDatosEstacionSiguiente['stop_id']+'_'+filaDatosEstacionSiguiente['line_number']+'_s'] = uriEnlace
    #else:
    #    if filaDatosEstacionActual['line_number'] == filaDatosEstacionAnterior['line_number'] and filaDatosEstacionActual['transportmean_name'] == filaDatosEstacionAnterior['transportmean_name']:
    #        gr.add ( ( generaUriEstacionMetro(filaDatosEstacionActual['transportmean_name'],filaDatosEstacionActual['line_number'],filaDatosEstacionActual['stop_name'],filaDatosEstacionActual['stop_id']) , uriTipoEnlaceAnterior, enlacesIndexados[filaDatosEstacionAnterior['stop_id']+'_'+filaDatosEstacionActual['stop_id']+'_'+filaDatosEstacionActual['line_number']]) )



def insertarPertenenciaLinea(gr,filaDatosEstacion):
    uriEstacion = estacionesIndexadas[filaDatosEstacion['transportmean_name']+'_'+filaDatosEstacion['stop_id']]
    gr.add ( (uriEstacion, uriEstacionPerteneceLinea,generaUriLinea(filaDatosEstacion['transportmean_name'],filaDatosEstacion['line_number'])) )


def insertarNuevaEstacion(gr,filaDatosEstacion):
    if not filaDatosEstacion['transportmean_name']+'_'+filaDatosEstacion['stop_id'] in estacionesIndexadas.keys():
        uriEstacion = generaUriEstacionMetro(filaDatosEstacion['transportmean_name'],filaDatosEstacion['line_number'],filaDatosEstacion['stop_name'],filaDatosEstacion['stop_id'])
        gr.add ( (uriEstacion, rdfSch.type, uriTipoEstacion) )
        gr.add ( (uriEstacion, rdfsSch.label, rdf.Literal(filaDatosEstacion['stop_name'].lower())))
        gr.add ( (uriEstacion, uriEstacionPerteneceLinea,generaUriLinea(filaDatosEstacion['transportmean_name'],filaDatosEstacion['line_number'])) )        
        if 'wheelchair_boarding' in filaDatosEstacion:
            if filaDatosEstacion['wheelchair_boarding'] == '1' or filaDatosEstacion['wheelchair_boarding'] == '2':
                gr.add ( (uriEstacion, uriTieneRampa,  rdf.Literal('True')) )
            else:
                gr.add ( (uriEstacion, uriTieneRampa, rdf.Literal('False')))
        else:
            gr.add ( (uriEstacion, uriTieneRampa, rdf.Literal('False')))   
        if 'stop_lat' in filaDatosEstacion:    
            gr.add ( (uriEstacion, geoSch.lat,  rdf.Literal(filaDatosEstacion['stop_lat'])) )
            gr.add ( (uriEstacion, geoSch.lon, rdf. Literal(filaDatosEstacion['stop_lon'])) )
          
        gr.add ( (uriEstacion, uriStopId,  rdf.Literal(filaDatosEstacion['stop_id'])) )  
        if 'stop_code' in filaDatosEstacion:    
            gr.add ( (uriEstacion, uriStopCode,  rdf.Literal(filaDatosEstacion['stop_code'])) )  
        if 'stop_desc' in filaDatosEstacion:    
            gr.add ( (uriEstacion, uriStopDesc,  rdf.Literal(filaDatosEstacion['stop_desc'])) )  
        if 'zone_id' in filaDatosEstacion:    
            gr.add ( (uriEstacion, uriZoneId,  rdf.Literal(filaDatosEstacion['zone_id'])) )   
        if 'location_type' in filaDatosEstacion:    
            gr.add ( (uriEstacion, uriLocationType,  rdf.Literal(filaDatosEstacion['location_type'])) )   
        if 'stop_timezone' in filaDatosEstacion:    
            gr.add ( (uriEstacion, uriStopTimeZone,  rdf.Literal(filaDatosEstacion['stop_timezone'])) )         
        estacionesIndexadas[filaDatosEstacion['transportmean_name']+'_'+filaDatosEstacion['stop_id']]=uriEstacion
    else:
        #el registro ya existe, insertamos la nueva linea a la que pertenece
        #uriEstacion = estacionesIndexadas[filaDatosEstacion['stop_id']]
        #gr.add ( (uriEstacion, uriEstacionPerteneceLinea,generaUriLinea(filaDatosEstacion['transportmean_name'],filaDatosEstacion['line_number'])) )
        insertarPertenenciaLinea(gr,filaDatosEstacion)

# transportmean_name,line_number,order_number,stop_id,stop_code,stop_name,stop_desc,stop_lat,stop_lon,zone_id,stop_url,location_type,parent_station,stop_timezone,wheelchair_boarding
with open('/mnt/c/Users/msalc/Qsync/docmaster/curso/programacion01/practicaObtencionDatos/scrapperMetro/scrapperMetro/stops.txt',newline='') as stopsfile:
    lineas = csv.DictReader(stopsfile, delimiter=",")
    for row in lineas:
        if not lineaAnterior is None:
            if row['transportmean_name']  != lineaAnterior['transportmean_name'] or ( row['transportmean_name']  == lineaAnterior['transportmean_name'] and  row['line_number']  != lineaAnterior['line_number'] ) :
                lineaAnterior = None
        if lineaAnterior is None:
            #primera linea del fichero
            lineasFicheroIndexadasClave[row['stop_id']] = row
            #uritipoLinea = rdf.URIRef(mediosTransporte[medioTransporte])
            insertarNuevaLinea(g,row['transportmean_name'],row['line_number'])
            if not row['transportmean_name']+'_'+row['stop_id'] in estacionesIndexadas.keys():
                insertarNuevaEstacion(g,row)
            else:
                insertarPertenenciaLinea(g,row)   

            lineaAnterior = row
            tipoMedioTransporteAnterior = row['transportmean_name']            
        else:           
            if not row['transportmean_name']+'_'+row['line_number'] in lineasIndexadas.keys():
                insertarNuevaLinea(g,row['transportmean_name'],row['line_number'])
           
            if not row['transportmean_name']+'_'+row['stop_id'] in estacionesIndexadas.keys():                
                insertarNuevaEstacion(g,row)
                lineasFicheroIndexadasClave[row['stop_id']] = row
            else:
                insertarPertenenciaLinea(g,row)

            if tipoExportacionEnlaces == 0:
                insertarEnlacePrevioSimplificado(g,row,lineaAnterior)
            else:
                insertarEnlacePrevio(g,row,lineaAnterior)   

            if tipoExportacionEnlaces == 0:
                insertarEnlaceSiguienteSimplificado(g,lineaAnterior,row)
            else:
                insertarEnlaceSiguiente(g,row,lineaAnterior)  
               

            lineaAnterior = row 
            tipoMedioTransporteAnterior = row['transportmean_name'] 


g.serialize(destination ="/mnt/c/Users/msalc/Qsync/docmaster/curso/programacion01/practicaObtencionDatos/scrapperMetro/scrapperMetro/estacionesRdf.xml", format = "xml")