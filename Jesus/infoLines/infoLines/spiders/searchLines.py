# -*- coding: utf-8 -*-
import scrapy


class SearchlinesSpider(scrapy.Spider):
    name = 'searchLines'
    allowed_domains = ['https://www.crtm.es']
    start_urls = ['https://www.crtm.es/tu-transporte-publico/metro/lineas/4__1___.aspx',
                  'https://www.crtm.es/tu-transporte-publico/metro/lineas/4__2___.aspx',
                  'https://www.crtm.es/tu-transporte-publico/metro/lineas/4__3___.aspx',
                  'https://www.crtm.es/tu-transporte-publico/metro/lineas/4__4___.aspx',
                  'https://www.crtm.es/tu-transporte-publico/metro/lineas/4__5___.aspx',
                  'https://www.crtm.es/tu-transporte-publico/metro/lineas/4__6___.aspx',
                  'https://www.crtm.es/tu-transporte-publico/metro/lineas/4__7___.aspx',
                  'https://www.crtm.es/tu-transporte-publico/metro/lineas/4__8___.aspx',
                  'https://www.crtm.es/tu-transporte-publico/metro/lineas/4__9___.aspx',
                  'https://www.crtm.es/tu-transporte-publico/metro/lineas/4__10___.aspx',
                  'https://www.crtm.es/tu-transporte-publico/metro/lineas/4__11___.aspx',
                  'https://www.crtm.es/tu-transporte-publico/metro/lineas/4__12___.aspx',
                  'https://www.crtm.es/tu-transporte-publico/metro/lineas/4__r___.aspx',
                  'https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas/5__1___.aspx',
                  'https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas/5__2___.aspx',
                  'https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas/5__3___.aspx',
                  'https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas/5__3_a__.aspx',
                  'https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas/5__4_a__.aspx',
                  'https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas/5__4_b__.aspx',
                  'https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas/5__5___.aspx',
                  'https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas/5__7___.aspx',
                  'https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas/5__8___.aspx',
                  'https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas/5__9___.aspx',
                  'https://www.crtm.es/tu-transporte-publico/cercanias-renfe/lineas/5__10___.aspx'
                  ]

    def parse(self, response):
        db = dict
        name_line = response.xpath('//div[@class="brdGris2"]/div/h4[@class="titu4"]/span/text()').extract_first()
        lines = []
        for row in response.xpath('//table[@class="tablaParadas"]/tbody/tr'):
            lines.append(row.xpath('.//td[1]/a/text()').extract_first())
        db[name_line] = lines
        self.log(name_line)
        self.log(lines)
        self.log(db)
        return db
