# -*- coding: utf-8 -*-
import scrapy
from  scrapperMetro.items import ScrappermetroItem
import re
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor

class BuscaestacionesmetroSpider(scrapy.Spider):
    name = 'buscaEstacionesMetro'
    allowed_domains = ['www.crtm.es']
    
    start_urls = ["https://www.crtm.es/tu-transporte-publico/metro/lineas.aspx",
                  "https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas.aspx",
                  "https://www.crtm.es/tu-transporte-publico/metro-ligero/lineas.aspx"
                  ]

    # start_urls = ["https://www.crtm.es/tu-transporte-publico/metro/lineas/4__1___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/metro/lineas/4__2___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/metro/lineas/4__3___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/metro/lineas/4__4___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/metro/lineas/4__5___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/metro/lineas/4__6___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/metro/lineas/4__7___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/metro/lineas/4__8___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/metro/lineas/4__9___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/metro/lineas/4__10___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/metro/lineas/4__11___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/metro/lineas/4__12___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/metro/lineas/4__r___.aspx"
    # "https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas/5__1___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas/5__2___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas/5__3___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas/5__3_a__.aspx",
    # "https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas/5__4_a__.aspx",
    # "https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas/5__4_b__.aspx",
    # "https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas/5__5___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas/5__7___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas/5__8___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas/5__9___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas/5__10___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/metro-ligero/lineas/10__51___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/metro-ligero/lineas/10__2___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/metro-ligero/lineas/10__3___.aspx",
    # "https://www.crtm.es/tu-transporte-publico/metro-ligero/lineas/10__4___.aspx"]

    # Extract link from this path only
     #Rule(
     #       LxmlLinkExtractor(restrict_xpaths=[
     #           '//div[@class="listaBotones logosRectangulo unaCol"]//a/@href'], allow_domains=['https://www.crtm.es/']), 
     #       callback='parse'
    #)


    def parse(self, response):
        #import pudb; pudb.set_trace()  
        #print(response.xpath('//div[@class="listaBotones logosRectangulo unaCol"]'))
        elementosURLs = response.xpath('//div[@class="listaBotones logosRectangulo unaCol"]//a')
        #next_page = response.xpath('//div[@class="listaBotones logosRectangulo unaCol"]//a/@href').get()
        if elementosURLs:
            for index, urlElement in enumerate(elementosURLs):
                next_page = urlElement.xpath('@href').get()
                if next_page:
                    yield Request(response.urljoin(next_page),callback=self.parse_stations)
        else:
            elementosURLs = response.xpath('//div[@class="listaBotones logosCuadrado dosCols"]//a')
            if elementosURLs:
                for index, urlElement in enumerate(elementosURLs):
                    next_page = urlElement.xpath('@href').get()
                    if next_page:
                        yield Request(response.urljoin(next_page),callback=self.parse_stations)

    def parse_stations(self, response):
            listaRetorno = []      
            elementosTabla = response.xpath('//table[@class="tablaParadas"]/tbody/tr/td[1]')
            for index, elementTR in enumerate(elementosTabla):
                item= ScrappermetroItem()
                elementos = (index, elementTR.xpath('a/text()').get(), elementTR.xpath('a/@href').get())
                item['tipoTransporte'] = re.findall('/([0-9]{1,2})__',response.request.url)[0]
                item['nombre_estacion'] = elementos[1].strip().lower()
                item['linea'] =  re.findall('/[0-9]{1,2}__([0123456789r]{1,2}[_]{0,1}[ab]{0,1})_',response.request.url)[0].replace('_','')
                item['orden'] = elementos[0]
                item['urlInformacionEstacion'] = elementos[2]
                listaRetorno.append(item)
            return listaRetorno
