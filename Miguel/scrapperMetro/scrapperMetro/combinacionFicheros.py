import csv
import os
from fuzzywuzzy import fuzz
import unicodedata
import re

#print(os.path.dirname(os.path.abspath(__file__)))

# leemos el fichero agregado tanto de metro como de las lineas de metro ligero y cercanias
# leemos el fichero ordenado por los campos tipoTransporte,linea,orden

def atoi(text):
    return int(text) if text.isdigit() else text
def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)',text) ]

with open('/mnt/c/Users/msalc/Qsync/docmaster/curso/programacion01/practicaObtencionDatos/scrapperMetro/scrapperMetro/estacionesMetro.csv',newline='') as csvfile:
    lineas = csv.DictReader(csvfile, delimiter=",")
    sortedLineas= sorted(lineas, key=lambda row:(int(row['tipoTransporte']),natural_keys(row['linea']),int(row['orden'])), reverse=False)

#funcion que nos permitira obtener unicamente las estaciones filtradas para las lineas de metro
def filterStationsMetro(row):
    if(row['stop_id'].startswith('est')):
        return True
    elif ( (row['stop_name'] == 'ACACIAS' or row['stop_name'] == 'SEVILLA' or row['stop_name'] == 'NOVICIADO' ) and row['location_type'] == '0' ):
        return True
    else:
        return False

def filterStationsCercanias(row):
    if(row['stop_id'].startswith('est')):
        return True
    elif ( row['stop_id'].startswith('par') and (row['parent_station'] is None or row['parent_station']=='')):
        return True
    else:
        return False

def filterStationsMetroLigero(row):
    if(row['stop_id'].startswith('est')):
        return True
    elif ( row['stop_id'].startswith('par') and (row['parent_station'] is None or row['parent_station']=='')):
        return True
    else:
        return False

#funcion para obtener los literales sin acentos 
def strip_accents_spain(string, accents=('COMBINING ACUTE ACCENT', 'COMBINING GRAVE ACCENT')):
    accents = set(map(unicodedata.lookup, accents))
    chars = [c for c in unicodedata.normalize('NFD', string) if c not in accents]
    return unicodedata.normalize('NFC', ''.join(chars))

# estructuras de datos auxiliares para acelerar el proceso de generacion del fichero definitivo de estaciones
# este diccionario guarda como clave los nombres normalizados y como valor una lista de valores  stop_id para esa clave
diccionario_nombres_estaciones_inverso_metro = {}
# este diccionario guarda como clave stop_id y como valor toda la informacion asociada a la estacion proveniente del fichero stops.txt
diccionario_claves_metro = {}
#este diccionario no se utiliza (seria importante si se quisiera tambien guardar los elementos que no son estaciones en el fichero definitivo) 
# y guarda como clave parent_stop_id y como valor una lista de registros provenientes del fichero stops.txt 
diccionario_claves_padre_metro = {}
# esta lista se guardan los elementos que no han podido ser indexados en las anteriores estructuras de datos
listaElementosFaltates = list()

with open('/mnt/c/Users/msalc/Qsync/docmaster/curso/programacion01/practicaObtencionDatos/scrapperMetro/scrapperMetro/ficherosMetro/stops.txt',newline='',encoding="utf-8-sig") as csvfileStopMetro:
    estacionesStopMetro = csv.DictReader(csvfileStopMetro, delimiter=",")
    #lineasStopMetro = filter(filterStations,estacionesStopMetro)
    for row in estacionesStopMetro:
        diccionario_claves_metro[row['stop_id']] = row
        if filterStationsMetro(row):           
            nombreEstacionNormalizada = strip_accents_spain(row['stop_name'].lower())
            if nombreEstacionNormalizada not in diccionario_nombres_estaciones_inverso_metro:
               listaClaves=[row['stop_id']]
               diccionario_nombres_estaciones_inverso_metro[nombreEstacionNormalizada] = listaClaves
            else:
                diccionario_nombres_estaciones_inverso_metro[nombreEstacionNormalizada].append(row['stop_id'])
        else:
            #diccionario_claves_padre_metro[row['parent_station']] = row  
            if not row['parent_station'] is None: 
                if row['parent_station'] not in diccionario_claves_padre_metro:
                    diccionario_claves_padre_metro[row['parent_station']] = list(row)
                else:
                    diccionario_claves_padre_metro[row['parent_station']].append(row)
            else:
                listaElementosFaltates.append(row)             


# estructuras de datos auxiliares para acelerar el proceso de generacion del fichero definitivo de estaciones
# este diccionario guarda como clave los nombres normalizados y como valor una lista de valores  stop_id para esa clave
diccionario_nombres_estaciones_inverso_cercanias = {}
# este diccionario guarda como clave stop_id y como valor toda la informacion asociada a la estacion proveniente del fichero stops.txt
diccionario_claves_cercanias = {}
#este diccionario no se utiliza (seria importante si se quisiera tambien guardar los elementos que no son estaciones en el fichero definitivo) 
# y guarda como clave parent_stop_id y como valor una lista de registros provenientes del fichero stops.txt 
diccionario_claves_padre_cercanias = {}


with open('/mnt/c/Users/msalc/Qsync/docmaster/curso/programacion01/practicaObtencionDatos/scrapperMetro/scrapperMetro/ficherosCercanias/stops.txt',newline='',encoding="utf-8-sig") as csvfileStopCercanias:
    estacionesStopCercanias = csv.DictReader(csvfileStopCercanias, delimiter=",")
    #lineasStopMetro = filter(filterStations,estacionesStopMetro)
    for row in estacionesStopCercanias:
        diccionario_claves_cercanias[row['stop_id']] = row
        if filterStationsCercanias(row):           
            nombreEstacionNormalizada = strip_accents_spain(row['stop_name'].lower())
            if nombreEstacionNormalizada not in diccionario_nombres_estaciones_inverso_cercanias:
               listaClaves=[row['stop_id']]
               diccionario_nombres_estaciones_inverso_cercanias[nombreEstacionNormalizada] = listaClaves
            else:
                diccionario_nombres_estaciones_inverso_cercanias[nombreEstacionNormalizada].append(row['stop_id'])
        else:
            #diccionario_claves_padre_cercanias[row['parent_station']] = row  
            if not row['parent_station'] is None: 
                if row['parent_station'] not in diccionario_claves_padre_cercanias:
                    diccionario_claves_padre_cercanias[row['parent_station']] = list(row)
                else:
                    diccionario_claves_padre_cercanias[row['parent_station']].append(row)
            else:
                listaElementosFaltates.append(row)     


# estructuras de datos auxiliares para acelerar el proceso de generacion del fichero definitivo de estaciones
# este diccionario guarda como clave los nombres normalizados y como valor una lista de valores  stop_id para esa clave
diccionario_nombres_estaciones_inverso_metro_ligero = {}
# este diccionario guarda como clave stop_id y como valor toda la informacion asociada a la estacion proveniente del fichero stops.txt
diccionario_claves_metro_ligero = {}
#este diccionario no se utiliza (seria importante si se quisiera tambien guardar los elementos que no son estaciones en el fichero definitivo) 
# y guarda como clave parent_stop_id y como valor una lista de registros provenientes del fichero stops.txt 
diccionario_claves_padre_metro_ligero = {}


with open('/mnt/c/Users/msalc/Qsync/docmaster/curso/programacion01/practicaObtencionDatos/scrapperMetro/scrapperMetro/ficherosMetroLigero/stops.txt',newline='',encoding="utf-8-sig") as csvfileStopMetroLigero:
    estacionesStopMetroLigero = csv.DictReader(csvfileStopMetroLigero, delimiter=",")
    #lineasStopMetro = filter(filterStations,estacionesStopMetro)
    for row in estacionesStopMetroLigero:
        diccionario_claves_metro_ligero[row['stop_id']] = row
        if filterStationsMetroLigero(row):           
            nombreEstacionNormalizada = strip_accents_spain(row['stop_name'].lower())
            if nombreEstacionNormalizada not in diccionario_nombres_estaciones_inverso_metro_ligero:
               listaClaves=[row['stop_id']]
               diccionario_nombres_estaciones_inverso_metro_ligero[nombreEstacionNormalizada] = listaClaves
            else:
                diccionario_nombres_estaciones_inverso_metro_ligero[nombreEstacionNormalizada].append(row['stop_id'])
        else:
            #diccionario_claves_padre_metro_ligero[row['parent_station']] = row  
            if not row['parent_station'] is None: 
                if row['parent_station'] not in diccionario_claves_padre_metro_ligero:
                    diccionario_claves_padre_metro_ligero[row['parent_station']] = list(row)
                else:
                    diccionario_claves_padre_metro_ligero[row['parent_station']].append(row)
            else:
                listaElementosFaltates.append(row)     


#print("numeroElementosFaltantes: "+str(len(listaElementosFaltates)))
with open('/mnt/c/Users/msalc/Qsync/docmaster/curso/programacion01/practicaObtencionDatos/scrapperMetro/scrapperMetro/stops.txt', mode='w') as fichero_salida:
    writer_fichero_salida = csv.writer(fichero_salida, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer_fichero_salida.writerow(['transportmean_name', 'line_number', 'order_number','stop_id','stop_code','stop_name','stop_desc','stop_lat','stop_lon','zone_id','stop_url','location_type','parent_station','stop_timezone','wheelchair_boarding'])
    for estacionesTransporte in sortedLineas:
        filaRegistro = None
        tipoTransporte = None
        if(estacionesTransporte['tipoTransporte'] == '4'):
            tipoTransporte = 'METRO'
            #procesamiento de lineas de metro           
            if(estacionesTransporte['nombre_estacion'] in diccionario_nombres_estaciones_inverso_metro):
                print('estacion metro encontrada '+estacionesTransporte['nombre_estacion'])
                filaRegistro = diccionario_claves_metro[diccionario_nombres_estaciones_inverso_metro[estacionesTransporte['nombre_estacion']][0]]
                print('fila metro encontada '+diccionario_claves_metro[diccionario_nombres_estaciones_inverso_metro[estacionesTransporte['nombre_estacion']][0]]['stop_name'])
            else:
                    #print('estacion no encontrada '+estacionesTransporte['nombre_estacion'])  
                    elementosProbables = {}
                    for nombresEstaciones in diccionario_nombres_estaciones_inverso_metro.keys():
                        partial_ratio = fuzz.partial_ratio(strip_accents_spain(estacionesTransporte['nombre_estacion']),nombresEstaciones)
                        if(partial_ratio > 85):
                            elementosProbables[nombresEstaciones] = partial_ratio
                    if len(elementosProbables) > 0:
                        maximo_peso_comprobacion = 0;
                        #for elementoProbable in elementosProbables:
                        #    print('elemento probable encontrado para  '+estacionesTransporte['nombre_estacion']+' denominado '+elementoProbable)  
                        keyMax = max(elementosProbables.keys(), key=(lambda k: elementosProbables[k]))
                        print('Elemento seleccionado metro '+keyMax+ ' para '+estacionesTransporte['nombre_estacion'])
                        if len(diccionario_nombres_estaciones_inverso_metro[keyMax]) == 1:
                            filaRegistro = diccionario_claves_metro[diccionario_nombres_estaciones_inverso_metro[keyMax][0]]
                            print('fila encontada metro '+diccionario_claves_metro[diccionario_nombres_estaciones_inverso_metro[keyMax][0]]['stop_name'])
                            #writer_fichero_salida.writerow(['METRO', estacionesTransporte['tipoTransporte'],estacionesTransporte['tipoTransporte'] ,filaRegistro['stop_id'],filaRegistro['stop_code'],filaRegistro['stop_name]',filaRegistro['stop_desc'],filaRegistro['stop_lat'],filaRegistro['stop_lon'],filaRegistro['zone_id'],filaRegistro['stop_url'],filaRegistro['location_type'],filaRegistro['parent_station'],filaRegistro['stop_timezone'],filaRegistro['wheelchair_boarding']])
                        else:
                            print('mas de una fila para metro')
                    else:
                        print('estacion no encontrada metro definitivamente '+estacionesTransporte['nombre_estacion']) 


        if(estacionesTransporte['tipoTransporte'] == '5'):
            #procesamiento de lineas de cercanias    
            tipoTransporte = 'CR'       
            if(estacionesTransporte['nombre_estacion'] in diccionario_nombres_estaciones_inverso_cercanias):
                print('estacion cercanias encontrada '+estacionesTransporte['nombre_estacion'])
                filaRegistro = diccionario_claves_cercanias[diccionario_nombres_estaciones_inverso_cercanias[estacionesTransporte['nombre_estacion']][0]]
                print('fila cercanias encontada '+diccionario_claves_cercanias[diccionario_nombres_estaciones_inverso_cercanias[estacionesTransporte['nombre_estacion']][0]]['stop_name'])
            else:
                    #print('estacion no encontrada '+estacionesTransporte['nombre_estacion'])  
                    elementosProbables = {}
                    for nombresEstaciones in diccionario_nombres_estaciones_inverso_cercanias.keys():
                        partial_ratio = fuzz.partial_ratio(strip_accents_spain(estacionesTransporte['nombre_estacion']),nombresEstaciones)
                        if(partial_ratio > 85):
                            elementosProbables[nombresEstaciones] = partial_ratio
                        else:
                            partial_ratio = fuzz.token_sort_ratio(strip_accents_spain(estacionesTransporte['nombre_estacion']),nombresEstaciones) 
                            if(partial_ratio > 85):
                                elementosProbables[nombresEstaciones] = partial_ratio
                    if len(elementosProbables) > 0:
                        maximo_peso_comprobacion = 0;
                        #for elementoProbable in elementosProbables:
                        #    print('elemento probable encontrado para  '+estacionesTransporte['nombre_estacion']+' denominado '+elementoProbable)  
                        keyMax = max(elementosProbables.keys(), key=(lambda k: elementosProbables[k]))
                        print('Elemento seleccionado cercanias '+keyMax+ ' para '+estacionesTransporte['nombre_estacion'])
                        if len(diccionario_nombres_estaciones_inverso_cercanias[keyMax]) == 1:
                            filaRegistro = diccionario_claves_cercanias[diccionario_nombres_estaciones_inverso_cercanias[keyMax][0]]
                            print('fila encontada cercanias '+diccionario_claves_cercanias[diccionario_nombres_estaciones_inverso_cercanias[keyMax][0]]['stop_name'])
                            #writer_fichero_salida.writerow(['METRO', estacionesTransporte['tipoTransporte'],estacionesTransporte['tipoTransporte'] ,filaRegistro['stop_id'],filaRegistro['stop_code'],filaRegistro['stop_name]',filaRegistro['stop_desc'],filaRegistro['stop_lat'],filaRegistro['stop_lon'],filaRegistro['zone_id'],filaRegistro['stop_url'],filaRegistro['location_type'],filaRegistro['parent_station'],filaRegistro['stop_timezone'],filaRegistro['wheelchair_boarding']])
                        else:
                            print('mas de una fila para cercanias')
                    else:
                        print('estacion no encontrada cercanias definitivamente '+estacionesTransporte['nombre_estacion']) 



        if(estacionesTransporte['tipoTransporte'] == '10'):
            #procesamiento de lineas de cercanias    
            tipoTransporte = 'ML'       
            if(estacionesTransporte['nombre_estacion'] in diccionario_nombres_estaciones_inverso_metro_ligero):
                print('estacion metro ligero encontrada '+estacionesTransporte['nombre_estacion'])
                filaRegistro = diccionario_claves_metro_ligero[diccionario_nombres_estaciones_inverso_metro_ligero[estacionesTransporte['nombre_estacion']][0]]
                print('fila metro ligero encontada '+diccionario_claves_metro_ligero[diccionario_nombres_estaciones_inverso_metro_ligero[estacionesTransporte['nombre_estacion']][0]]['stop_name'])
            else:
                    #print('estacion no encontrada '+estacionesTransporte['nombre_estacion'])  
                    elementosProbables = {}
                    for nombresEstaciones in diccionario_nombres_estaciones_inverso_metro_ligero.keys():
                        partial_ratio = fuzz.partial_ratio(strip_accents_spain(estacionesTransporte['nombre_estacion']),nombresEstaciones)
                        if(partial_ratio > 85):
                            elementosProbables[nombresEstaciones] = partial_ratio
                        else:
                            partial_ratio = fuzz.token_sort_ratio(strip_accents_spain(estacionesTransporte['nombre_estacion']),nombresEstaciones) 
                            if(partial_ratio > 85):
                                elementosProbables[nombresEstaciones] = partial_ratio
                    if len(elementosProbables) > 0:
                        maximo_peso_comprobacion = 0;
                        #for elementoProbable in elementosProbables:
                        #    print('elemento probable encontrado para  '+estacionesTransporte['nombre_estacion']+' denominado '+elementoProbable)  
                        keyMax = max(elementosProbables.keys(), key=(lambda k: elementosProbables[k]))
                        print('Elemento seleccionado metro_ligero '+keyMax+ ' para '+estacionesTransporte['nombre_estacion'])
                        if len(diccionario_nombres_estaciones_inverso_metro_ligero[keyMax]) == 1:
                            filaRegistro = diccionario_claves_metro_ligero[diccionario_nombres_estaciones_inverso_metro_ligero[keyMax][0]]
                            print('fila encontada metro ligero '+diccionario_claves_metro_ligero[diccionario_nombres_estaciones_inverso_metro_ligero[keyMax][0]]['stop_name'])
                            #writer_fichero_salida.writerow(['METRO', estacionesTransporte['tipoTransporte'],estacionesTransporte['tipoTransporte'] ,filaRegistro['stop_id'],filaRegistro['stop_code'],filaRegistro['stop_name]',filaRegistro['stop_desc'],filaRegistro['stop_lat'],filaRegistro['stop_lon'],filaRegistro['zone_id'],filaRegistro['stop_url'],filaRegistro['location_type'],filaRegistro['parent_station'],filaRegistro['stop_timezone'],filaRegistro['wheelchair_boarding']])
                        else:
                            print('mas de una fila para metro ligero intento obtener la estacion')
                            for estacionesCandidatas in diccionario_nombres_estaciones_inverso_metro_ligero[keyMax]:
                                if estacionesCandidatas.startswith('est'):
                                    filaRegistro = diccionario_claves_metro_ligero[estacionesCandidatas]
                                    break;
                    else:
                        print('estacion no encontrada metro ligero definitivamente '+estacionesTransporte['nombre_estacion']) 


        if not filaRegistro is None:
            writer_fichero_salida.writerow([tipoTransporte, estacionesTransporte['linea'],estacionesTransporte['linea']+'_'+estacionesTransporte['orden'] ,filaRegistro['stop_id'],filaRegistro['stop_code'],filaRegistro['stop_name'],filaRegistro['stop_desc'],filaRegistro['stop_lat'],filaRegistro['stop_lon'],filaRegistro['zone_id'],filaRegistro['stop_url'],filaRegistro['location_type'],filaRegistro['parent_station'],filaRegistro['stop_timezone'],filaRegistro['wheelchair_boarding']])
        else:
            print('error escribiendo fichero')    






