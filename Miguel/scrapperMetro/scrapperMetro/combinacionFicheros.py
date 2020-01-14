import csv
import os
from fuzzywuzzy import fuzz
import unicodedata
import re

#print(os.path.dirname(os.path.abspath(__file__)))

#funcion para realizar el ordenamiento natural de las claves, no el lexicografico
def atoi(text):
    return int(text) if text.isdigit() else text
def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)',text) ]

# leemos el fichero agregado tanto de metro como de las lineas de metro ligero y cercanias
# leemos el fichero obtenido por el scrapper ordenado por los campos tipoTransporte,linea,orden
# pese a que el nombre del fichero se denomina estacionesMetro.csv, este fichero tiene todas las lineas para metro, metro ligero y cercanias
with open('/mnt/c/Users/msalc/Qsync/docmaster/curso/programacion01/practicaObtencionDatos/scrapperMetro/scrapperMetro/estacionesMetro.csv',newline='') as csvfile:
    lineas = csv.DictReader(csvfile, delimiter=",")
    sortedLineas= sorted(lineas, key=lambda row:(int(row['tipoTransporte']),natural_keys(row['linea']),int(row['orden'])), reverse=False)

#funcion que nos permitira obtener unicamente las estaciones filtradas para las lineas de metro quitando las paradas
def filterStationsMetro(row):
    if(row['stop_id'].startswith('est')):
        return True
    elif ( (row['stop_name'] == 'ACACIAS' or row['stop_name'] == 'SEVILLA' or row['stop_name'] == 'NOVICIADO' ) and row['location_type'] == '0' ):
        return True
    else:
        return False

#funcion que nos permitira obtener unicamente las estaciones filtradas para cercanias quitando las paradas
def filterStationsCercanias(row):
    if(row['stop_id'].startswith('est')):
        return True
    elif ( row['stop_id'].startswith('par') and (row['parent_station'] is None or row['parent_station']=='')):
        return True
    else:
        return False

#funcion que nos permitira obtener unicamente las estaciones filtradas para metro ligero quitando las paradas
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
    retorno = unicodedata.normalize('NFC', ''.join(chars))
    retorno = retorno.replace(' - ',' ')
    return retorno

# estructuras de datos auxiliares para acelerar el proceso de generacion del fichero definitivo de estaciones
# este diccionario guarda como clave los nombres normalizados y como valor una lista de valores  stop_id para esa clave
# notar que frente a una posible colision de nombres (es decir, dos registros con el mismo nombre de estacion)
# el diccionario solo almacena una, la ultima leida. No obstante, debido a que a la hora de cargar este fichero solo hemos leido las
# estaciones y no las paradas (registros con parent_station null o que comienzan con 'est_' en su nombre), esta colision no se da
# y garantizamos que para el mismo nombre de estacion siempre se nos da el mismo 'stop_id'
diccionario_nombres_estaciones_inverso_metro = {}
# este diccionario guarda como clave stop_id y como valor toda la informacion asociada a la estacion proveniente del fichero stops.txt
diccionario_claves_metro = {}
#este diccionario no se utiliza (seria importante si se quisiera tambien guardar los elementos que no son estaciones en el fichero definitivo) 
# y guarda como clave parent_stop_id y como valor una lista de registros provenientes del fichero stops.txt 
diccionario_claves_padre_metro = {}
# esta lista se guardan los elementos que no han podido ser indexados en las anteriores estructuras de datos
# al finalizar el proceso de combinacion esta lista debería estar vacia completamente
listaElementosFaltates = list()

# leemos el fichero stops.txt de metro original
with open('/mnt/c/Users/msalc/Qsync/docmaster/curso/programacion01/practicaObtencionDatos/scrapperMetro/scrapperMetro/ficherosMetro/stops.txt',newline='',encoding="utf-8-sig") as csvfileStopMetro:
    estacionesStopMetro = csv.DictReader(csvfileStopMetro, delimiter=",")
    #lineasStopMetro = filter(filterStations,estacionesStopMetro)
    for row in estacionesStopMetro:
        # indexamos cada una de las filas por stop_id en un diccionario
        diccionario_claves_metro[row['stop_id']] = row
        # comprobamos si la linea cumple con el criterio de estacion y desechamos el resto
        if filterStationsMetro(row):    
            #si cumple con el criterio, normalizamos en nombre de la estacion para facilitar el proceso de busqueda       
            nombreEstacionNormalizada = strip_accents_spain(row['stop_name'].lower())
            # comprobamos si el nombre de la estacion lo hemos metido en el diccionario inverso indexado por nombre de estacion y que tiene
            # como valor una lista de stops_id con ese mismo nombre normalizado            
            if nombreEstacionNormalizada not in diccionario_nombres_estaciones_inverso_metro:
               listaClaves=[row['stop_id']]
               diccionario_nombres_estaciones_inverso_metro[nombreEstacionNormalizada] = listaClaves
            else:
                diccionario_nombres_estaciones_inverso_metro[nombreEstacionNormalizada].append(row['stop_id'])
        else:
            #diccionario_claves_padre_metro[row['parent_station']] = row  
            # si no cumple con el criterio de estacion, introducimos este registro en una estructura de datos
            # indexada por parent_station para asi poder recuperar las paradas asociadas a una estacion
            # al final esta estructura de datos no ha hecho falta porque la practica solo pide obtener las
            # estaciones
            if not row['parent_station'] is None: 
                if row['parent_station'] not in diccionario_claves_padre_metro:
                    diccionario_claves_padre_metro[row['parent_station']] = list(row)
                else:
                    diccionario_claves_padre_metro[row['parent_station']].append(row)
            else:
                listaElementosFaltates.append(row)             


# estructuras de datos auxiliares para acelerar el proceso de generacion del fichero definitivo de estaciones
# este diccionario guarda como clave los nombres normalizados y como valor una lista de valores  stop_id para esa clave
# notar que frente a una posible colision de nombres (es decir, dos registros con el mismo nombre de estacion)
# el diccionario solo almacena una, la ultima leida. No obstante, debido a que a la hora de cargar este fichero solo hemos leido las
# estaciones y no las paradas (registros con parent_station null o que comienzan con 'est_' en su nombre), esta colision no se da
# y garantizamos que para el mismo nombre de estacion siempre se nos da el mismo 'stop_id'
diccionario_nombres_estaciones_inverso_cercanias = {}
# este diccionario guarda como clave stop_id y como valor toda la informacion asociada a la estacion proveniente del fichero stops.txt
diccionario_claves_cercanias = {}
#este diccionario no se utiliza (seria importante si se quisiera tambien guardar los elementos que no son estaciones en el fichero definitivo) 
# y guarda como clave parent_stop_id y como valor una lista de registros provenientes del fichero stops.txt 
diccionario_claves_padre_cercanias = {}

# repetimos la lectura del fichero stops.txt con el mismo algoritmo que el comentado aarriba para los ficheros de cercanias
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


# comentario general de mejora: al final se ha metido cada fichero stops.txt en sus propios diccionarios diferenciandolos por medio de transporte
# por si existen claves primarias 'stops_txt' mezcladas en ambas. Esto al final no ha sido asi y los diccionarios de claves podrían hacerse comunes
# no obstante, los diccionarios de claves inversos si que conviene tenerlos separados en 3 diccionarios distintos

# estructuras de datos auxiliares para acelerar el proceso de generacion del fichero definitivo de estaciones
# este diccionario guarda como clave los nombres normalizados y como valor una lista de valores  stop_id para esa clave
# notar que frente a una posible colision de nombres (es decir, dos registros con el mismo nombre de estacion)
# el diccionario solo almacena una, la ultima leida. Todas las posibles claves con el mismo nombre se almacenan en una lista asociada
# a esa clave, y a la hora de elegir una de las posibles claves asociadas a un nombre, siempre nos quedamos con el primer elemento
# que aparece en la lista
diccionario_nombres_estaciones_inverso_metro_ligero = {}
# este diccionario guarda como clave stop_id y como valor toda la informacion asociada a la estacion proveniente del fichero stops.txt
diccionario_claves_metro_ligero = {}
#este diccionario no se utiliza (seria importante si se quisiera tambien guardar los elementos que no son estaciones en el fichero definitivo) 
# y guarda como clave parent_stop_id y como valor una lista de registros provenientes del fichero stops.txt 
diccionario_claves_padre_metro_ligero = {}

# repetimos la lectura del fichero stops.txt con el mismo algoritmo que el comentado arriba para los ficheros de metro ligero
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

# una vez leido todo, la lista de elementos faltantes deberia estar vacia
# si no lo esta, es que hay algo inconsistente en los ficheros stops.txt o el codigo ha hecho algo incorrecto
#print("numeroElementosFaltantes: "+str(len(listaElementosFaltates)))

# una vez leidos e indexados los tres ficheros stops.txt, procederemos a general el fichero stops.txt de la practica mezclando los 3 ficheros stops
# con el fichero de paradas obtenido por el scrapper. En primer lugar abrimos el fichero para escrutura
with open('/mnt/c/Users/msalc/Qsync/docmaster/curso/programacion01/practicaObtencionDatos/scrapperMetro/scrapperMetro/stops.txt', mode='w') as fichero_salida:
    writer_fichero_salida = csv.writer(fichero_salida, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer_fichero_salida.writerow(['transportmean_name', 'line_number', 'order_number','stop_id','stop_code','stop_name','stop_desc','stop_lat','stop_lon','zone_id','stop_url','location_type','parent_station','stop_timezone','wheelchair_boarding'])
    # leemos el fichero obtenido del scrapper ordenado por medio de transporte, linea y posicion
    for estacionesTransporte in sortedLineas:
        filaRegistro = None
        tipoTransporte = None
        # si el tipo de transporte asociado en el fichero del scrapper es metro
        if(estacionesTransporte['tipoTransporte'] == '4'):
            tipoTransporte = 'METRO'
            #procesamiento de lineas de metro           
            # ahora buscamos el nombre de la estacion el el diccionario que como clave tiene el nombre de la estacion normalizada
            # y como valor el 'stop_id' correspondiente
            if(estacionesTransporte['nombre_estacion'] in diccionario_nombres_estaciones_inverso_metro):
                # si nos encontramos el nombre directamente en el diccionario, obtenemos su fila asociada
                # seguimos haciendo notar que el diccionario diccionario_nombres_estaciones_inverso_metro solo almacena un unico stop_id
                # por nombre, con lo que para un nombre de estacion en particular siempre se seleccionara el mismo registro
                print('estacion metro encontrada '+estacionesTransporte['nombre_estacion'])
                filaRegistro = diccionario_claves_metro[diccionario_nombres_estaciones_inverso_metro[estacionesTransporte['nombre_estacion']][0]]
                print('fila metro encontada '+diccionario_claves_metro[diccionario_nombres_estaciones_inverso_metro[estacionesTransporte['nombre_estacion']][0]]['stop_name'])
            else:
                    #print('estacion no encontrada '+estacionesTransporte['nombre_estacion'])  
                    # no nos hemos encontrado el nombre de la estacion directamente, pasamos a realizar una comprobación "borrosa"
                    # de la cadena de caracteres que lleva el nombre de la estacion. Para ello recorremos todos los nombres de estacion indexados
                    # y vamos comparandolos con la libreria wuzzyfuzzy que implementa diversos algoritmos que dan una métrica
                    # entre 0 y 100 de la similitud entre dos cadenas de caracteres. Si esta similitud supera un umbran, almacenamos en un diccionario
                    # el nombre de la estacion coincidente y la similitud, para luego elegir aquel que tenga mayor similitud como estacion asociada
                    elementosProbables = {}
                    for nombresEstaciones in diccionario_nombres_estaciones_inverso_metro.keys():
                        partial_ratio = fuzz.ratio(strip_accents_spain(estacionesTransporte['nombre_estacion']),nombresEstaciones)
                        if(partial_ratio > 85):
                            elementosProbables[nombresEstaciones] = partial_ratio
                        else:
                            partial_ratio = fuzz.token_sort_ratio(strip_accents_spain(estacionesTransporte['nombre_estacion']),nombresEstaciones) 
                            if(partial_ratio > 85):
                                # penalizamos ligeramente el peso de esta busqueda
                                elementosProbables[nombresEstaciones] = partial_ratio*0.9
                            else:
                                partial_ratio = fuzz.partial_ratio(strip_accents_spain(estacionesTransporte['nombre_estacion']),nombresEstaciones) 
                                if(partial_ratio > 85):
                                    # penalizamos todavia mas el peso de esta busqueda
                                    elementosProbables[nombresEstaciones] = partial_ratio*0.8
                    # vemos si la busqueda por todas las estacionnes ha dado positivo. Nos quedamos con el elemento
                    # que tiene la máxima verosimilitud
                    if len(elementosProbables) > 0:
                        maximo_peso_comprobacion = 0
                        #for elementoProbable in elementosProbables:
                        #    print('elemento probable encontrado para  '+estacionesTransporte['nombre_estacion']+' denominado '+elementoProbable) 
                        # obtenemos el elemento con mas peso como candidato para representar a la estación obtenida por el scrapper 
                        keyMax = max(elementosProbables.keys(), key=(lambda k: elementosProbables[k]))
                        print('Elemento seleccionado metro '+keyMax+ ' para '+estacionesTransporte['nombre_estacion'])
                        # si la busqueda del maximo ha dado un unico registor, obtenemos la fila asociada a la estacion para grabarla
                        # en el fichero stops.txt definitivo
                        if len(diccionario_nombres_estaciones_inverso_metro[keyMax]) == 1:
                            filaRegistro = diccionario_claves_metro[diccionario_nombres_estaciones_inverso_metro[keyMax][0]]
                            print('fila encontada metro '+diccionario_claves_metro[diccionario_nombres_estaciones_inverso_metro[keyMax][0]]['stop_name'])
                            #writer_fichero_salida.writerow(['METRO', estacionesTransporte['tipoTransporte'],estacionesTransporte['tipoTransporte'] ,filaRegistro['stop_id'],filaRegistro['stop_code'],filaRegistro['stop_name]',filaRegistro['stop_desc'],filaRegistro['stop_lat'],filaRegistro['stop_lon'],filaRegistro['zone_id'],filaRegistro['stop_url'],filaRegistro['location_type'],filaRegistro['parent_station'],filaRegistro['stop_timezone'],filaRegistro['wheelchair_boarding']])
                        else:
                            # por aqui no deberia pasar con la información que hay para metro
                            print('mas de una fila para metro')
                    else:
                        # por aqui no deberia pasar con la informacion que hay para metro
                        print('estacion no encontrada metro definitivamente '+estacionesTransporte['nombre_estacion']) 

        # repetimos el mismo proceso de comparacion hecho para el metro si el registro asociado es de cercanias
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
                        partial_ratio = fuzz.ratio(strip_accents_spain(estacionesTransporte['nombre_estacion']),nombresEstaciones)
                        if(partial_ratio > 85):
                            elementosProbables[nombresEstaciones] = partial_ratio
                        else:
                            partial_ratio = fuzz.token_sort_ratio(strip_accents_spain(estacionesTransporte['nombre_estacion']),nombresEstaciones) 
                            if(partial_ratio > 85):
                                elementosProbables[nombresEstaciones] = partial_ratio*0.9
                            else:
                                partial_ratio = fuzz.partial_ratio(strip_accents_spain(estacionesTransporte['nombre_estacion']),nombresEstaciones) 
                                if(partial_ratio > 85):
                                    elementosProbables[nombresEstaciones] = partial_ratio*0.8
                    if len(elementosProbables) > 0:
                        maximo_peso_comprobacion = 0
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


        # repetimos el mismo proceso de comparacion hecho para el metro si el registro asociado es de metro ligero
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
                        maximo_peso_comprobacion = 0
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
                            # en caso de encontrarnos un registro que sea parada y estacion con la misma similitud, elegimos la estacion
                            # frente a la parada (asi, dado un nombre de estacion que tiene varias paradas devolvemos siempre el mismo identificador)
                            for estacionesCandidatas in diccionario_nombres_estaciones_inverso_metro_ligero[keyMax]:
                                if estacionesCandidatas.startswith('est'):
                                    filaRegistro = diccionario_claves_metro_ligero[estacionesCandidatas]
                                    break
                    else:
                        print('estacion no encontrada metro ligero definitivamente '+estacionesTransporte['nombre_estacion']) 

        # comentario general de mejora: los tres ifs anteriores se podrían refactorizada en una unica funcion que fuese invocada
        # teniendo como parametros los diccionarios que hemos utilizado praa indexar el fichero original
        # otra opcion seria usar pandas e ir relizando joins entre los dos ficheros, pero se ha preferido un enfoque mas manual
        # para practicar python y hacer las "joins" algoritmicamente (lo cual, evidentemente, es mas "doloroso" que utilizar pandas directamente). Además, de esta forma podemos realizar comprobaciones mas
        # flexibles entre los nombres de las estaciones.
        

        # una vez obtenida la informacion de la estacion mas similar para el registro obtenido del scrapper,
        # pasamos a copiar dicho registro al fichero stops.txt con el formato pedido en la practica
        if not filaRegistro is None:
            writer_fichero_salida.writerow([tipoTransporte, estacionesTransporte['linea'],estacionesTransporte['linea']+'_'+estacionesTransporte['orden'] ,filaRegistro['stop_id'],filaRegistro['stop_code'],filaRegistro['stop_name'],filaRegistro['stop_desc'],filaRegistro['stop_lat'],filaRegistro['stop_lon'],filaRegistro['zone_id'],filaRegistro['stop_url'],filaRegistro['location_type'],filaRegistro['parent_station'],filaRegistro['stop_timezone'],filaRegistro['wheelchair_boarding']])
        else:
            print('error escribiendo fichero')    






