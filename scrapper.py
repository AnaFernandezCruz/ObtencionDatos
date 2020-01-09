'''
Dado que los archivos stops.txt de cada medio de transporte no contienen el orden del itinerario de las líneas a las que pertenece cada estación  es necesario
buscar esa información con un scrapper en el link https://www.crtm.es/tu-transporte-publico.aspx

TODO:
    1. Acceder al enlace Líneas de cada medio de transporte (M, ML, C)
    2. Una vez hemos accedido a ese enlace habrá que recorrer todas las líneas, acceder a su contenido y obtener la ordenación de las estaciones
'''

import requests
from bs4 import BeautifulSoup
import re

def getLinks(url, transporte, pages):
    url_transporte =  str(url) + str(transporte) + "/lineas.aspx"
    html = requests.get(url_transporte)
    bsObj = BeautifulSoup(html.text, "html.parser")
    if "cercanias" in transporte:
        atributo = "listaBotones logosRectangulo unaCol"
    else:
        atributo = "listaBotones logosCuadrado dosCols"
    for link in bsObj.find("div", {"class": atributo}).findAll("a", href=re.compile("^(/tu-transporte-publico/" + str(transporte) + "/lineas/)((?!:).)*$")):
        if 'href' in link.attrs:
            if link.attrs['href'] not in pages:
                newPage = link.attrs['href']
                print('------' + newPage)
                pages.add(newPage)
    
    return pages

metodos_transporte = ["metro", "metro-ligero", "cercanias-renfe"]
url = "https://www.crtm.es/tu-transporte-publico/"

for transporte in metodos_transporte:
    paginas = set()
    paginas = getLinks(url, transporte, paginas)
    print('------------')
    print(transporte)
    print(paginas)
    print('------------')
    