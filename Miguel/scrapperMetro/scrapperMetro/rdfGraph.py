import rdflib as rdf
import csv
import unicodedata

g = rdf.Graph ()

prefijoUris = 'http://www.urlontologiametro.com/'

sch = rdf.Namespace('https://schema.org')
manto = rdf.Namespace('http://com.vortic3.MANTO#')
rdfSch = rdf.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
uriLocal = rdf.Namespace('http://www.meinventoesto.com/')
rdfsSch = rdf.Namespace('http://www.w3.org/2000/01/rdf-schema#')
geoSch = rdf.Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')

# esta variable controla el tipo de exportacion en rdf
# si es 0 la relacion entre estacion siguiente/anterior no tendra como atributo la linea a la que pertenece esa relacion y tendra tanto como
# sujeto como predicado una estacion (el rdf sale mas reducido pero mucho más simple, es la opción por defecto que se recomienda para generar el fichero rdf)
# si es 1 la relacion si que tendra la linea y cada enlace entre estaciones tendra su propia uri. Habrá dos tipos de enlaces: enlaces con la
# estacion anterior y enlace con la estacion siguiente. Cada enlace tendra su uri.
tipoExportacionEnlaces = 0
# diccionario con las uris para cada tipo de medio de transporte
mediosTransporte = {'METRO' : prefijoUris+'medioTransporte'+'#metro', 'CR':prefijoUris+'medioTransporte'+'#cercanias','ML':prefijoUris+'medioTransporte'+'#metroLigero'}
# uri para indicar el tipo de un objeto de tipo medio de trasporte
uriTipoMedioTransporte = uriLocal.tipoMedioTransporte  #rdf.URIRef(prefijoUris+'tipoMedioTransporte')
# uri para indicar el tipo de un objeto de tipo linea
uriTipoLinea =  uriLocal.linea #rdf.URIRef(prefijoUris+'linea')
# uri para indicar que una entidad es de tipo estacion
uriTipoEstacion = uriLocal.estacion #rdf.URIRef(prefijoUris+'estacion')
# uri para indicar que una relacion entre estaciones es de tipo enlaceSiguiente (usada en tipoExportacionEnlaces = 1)
uriTipoEnlaceSiguiente = uriLocal.enlaceSiguiente #rdf.URIRef(prefijoUris+'enlaceSiguiente')
# uri para indicar que una relacion entre estaciones es de tipo enlaceAnterior (usada en tipoExportacionEnlaces = 1)
uriTipoEnlaceAnterior = uriLocal.enlaceAnterior  #rdf.URIRef(prefijoUris+'enlaceAnterior')
# uri para indicar el predicado que asocia una estacion con su enlace
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

#generamos las triplas que modelan los tipos de medio de transporte (cercanias, metro y metro ligero)
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

# funcion que genera la URI de una linea
def generaUriLinea(tipoMedioTransporte,nombreLinea):
    return rdf.URIRef(prefijoUris+'lineas/'+tipoMedioTransporte.lower()+'/'+nombreLinea.lower())

# funcion que genera la URI de un medio de transporte
def generaUriMedioTransporte(tipoMedioTransporte):
    return rdf.URIRef(mediosTransporte[tipoMedioTransporte])

# funcion que genera la URI de una estacion (no tiene que ser de tipo estacion de metro)
def generaUriEstacionMetro(tipoMedioTransporte,nombreLinea,nombreEstacion,idEstacion):
    return rdf.URIRef(prefijoUris+'estaciones/'+tipoMedioTransporte.lower()+'/'+idEstacion+'/'+strip_accents_spain(nombreEstacion.lower()))

# funcion que genera una URI unica para cada enlace entre estaciones  (usada en tipoExportacionEnlaces = 1)
def generaUriEnlace():
    global secuencialIdentificadorEnlaces
    secuencialIdentificadorEnlaces=secuencialIdentificadorEnlaces+1
    return rdf.URIRef(prefijoUris+'enlaces/'+str(secuencialIdentificadorEnlaces))
    
# funcion que inserta las triplas que definen una linea 
def insertarNuevaLinea(gr,tipoMedioTransporte,nombreLinea):
    if not tipoMedioTransporte.lower()+'_'+nombreLinea.lower() in lineasIndexadas.keys():
        uriLinea= generaUriLinea(tipoMedioTransporte,nombreLinea)
        uriMedioTransporte = generaUriMedioTransporte(tipoMedioTransporte)
        gr.add ( (uriLinea, rdfSch.type, uriTipoLinea) )
        gr.add ( (uriLinea, rdfsSch.label, rdf.Literal(' linea de '+tipoMedioTransporte.lower()+' '+nombreLinea.lower())) )
        gr.add ( (uriLinea,uriMedioTransporteAsociado, uriMedioTransporte) )
        lineasIndexadas[tipoMedioTransporte.lower()+'_'+nombreLinea.lower()] = uriLinea

# funcion que inserta un enlace entre una estacion y la estacion anterior cuando tipoExportacionEnlaces = 0
# el enlace se crea unicamente cuando tanto la estacion actual como la siguiente  pertenecen a la misma linea y al mismo medio de tranporte
def insertarEnlacePrevioSimplificado(gr,filaDatosEstacionActual,filaDatosEstacionAnterior):
    if not filaDatosEstacionAnterior['stop_id']+'_'+filaDatosEstacionActual['stop_id']+'_'+filaDatosEstacionActual['line_number']+'_s' in enlacesIndexados.keys():
        if filaDatosEstacionActual['line_number'] == filaDatosEstacionAnterior['line_number'] and filaDatosEstacionActual['transportmean_name'] == filaDatosEstacionAnterior['transportmean_name']:
            gr.add ( ( generaUriEstacionMetro(filaDatosEstacionActual['transportmean_name'],filaDatosEstacionActual['line_number'],filaDatosEstacionActual['stop_name'],filaDatosEstacionActual['stop_id']) , uriTipoEnlaceAnterior, generaUriEstacionMetro(filaDatosEstacionAnterior['transportmean_name'],filaDatosEstacionAnterior['line_number'],filaDatosEstacionAnterior['stop_name'],filaDatosEstacionAnterior['stop_id'])) )
            enlacesIndexados[filaDatosEstacionAnterior['stop_id']+'_'+filaDatosEstacionActual['stop_id']+'_'+filaDatosEstacionActual['line_number']+'_s'] = '1'


# funcion que inserte un enlace entre una estacion y la estacion anterior cuando tipoExportacionEnlaces = 1
# cada enlace previo es un objeto con su propia URL y con propiedades la estacion anterior y la linea a la que pertenece el enlace
# esta entidad es a su vez objeto de un predicado indicando estacion anterior con sujeto la estacion actual
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


# funcion que inserta un enlace entre una estacion y la estacion siguiente cuando tipoExportacionEnlaces = 0
# el enlace se crea unicamente cuando tanto la estacion actual como la siguiente  pertenecen a la misma linea y al mismo medio de tranporte
def insertarEnlaceSiguienteSimplificado(gr,filaDatosEstacionActual,filaDatosEstacionSiguiente):
    if not filaDatosEstacionActual['stop_id']+'_'+filaDatosEstacionSiguiente['stop_id']+'_'+filaDatosEstacionSiguiente['line_number'] in enlacesIndexados.keys():
        if filaDatosEstacionActual['line_number'] == filaDatosEstacionSiguiente['line_number'] and filaDatosEstacionActual['transportmean_name'] == filaDatosEstacionSiguiente['transportmean_name']:
            gr.add ( ( generaUriEstacionMetro(filaDatosEstacionActual['transportmean_name'],filaDatosEstacionActual['line_number'],filaDatosEstacionActual['stop_name'],filaDatosEstacionActual['stop_id']) , uriTipoEnlaceSiguiente, generaUriEstacionMetro(filaDatosEstacionSiguiente['transportmean_name'],filaDatosEstacionSiguiente['line_number'],filaDatosEstacionSiguiente['stop_name'],filaDatosEstacionSiguiente['stop_id'])) )
            enlacesIndexados[filaDatosEstacionActual['stop_id']+'_'+filaDatosEstacionSiguiente['stop_id']+'_'+filaDatosEstacionSiguiente['line_number']] = '1'

# funcion que inserte un enlace entre una estacion y la estacion siguiente cuando tipoExportacionEnlaces = 1
# cada enlace siguiente es un objeto con su propia URL y con propiedades la estacion siguiente y la linea a la que pertenece el enlace
# esta entidad es a su vez objeto de un predicado indicando estacion siguiente con sujeto la estacion actual
#el enlace se crea unicamente cuando tanto la estacion actual como la siguiente  pertenecen a la misma linea y al mismo medio de tranporte
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


# funcion que inserta la linea a la que pertenece un enlace entre estaciones cuando tipoExportacionEnlaces = 1
# cuando tipoExportacionEnlaces = 0 esa informacion no se almacena en la tripla
def insertarPertenenciaLinea(gr,filaDatosEstacion):
    uriEstacion = estacionesIndexadas[filaDatosEstacion['transportmean_name']+'_'+filaDatosEstacion['stop_id']]
    gr.add ( (uriEstacion, uriEstacionPerteneceLinea,generaUriLinea(filaDatosEstacion['transportmean_name'],filaDatosEstacion['line_number'])) )

# funcion que inserta todas las triplas asociadas a una estacion con todos sus atributos
# como parametro de entrada tiene un grafo y una fila leida del fichero stops.txt 
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
# codigo que a partir del fichero stops.txt generado de mezclar los ficheros stops.txt de cada medio de transporte y del obtenido por el scrapper
# genera el grafo rdf con toda la información de las estaciones y las lineas a las que pertenece
with open('./stops.txt',newline='') as stopsfile:
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


g.serialize(destination ="./estacionesRdf.xml", format = "xml")