import scrapy
from datetime import datetime
import pytz
from scrapy.crawler import CrawlerProcess
import filtros_list



class TelegramSpider(scrapy.Spider):
    name = "telegram"
    start_urls = filtros_list.canal

    resultados = []
        
    def parse(self, response):
        filtros = filtros_list.filtros

        tz_ny = pytz.timezone('US/Eastern')
        hoy = datetime.now(tz_ny).strftime("%Y-%m-%d")
        
        mensajes = response.css(".tgme_widget_message_wrap")

        for mensaje in mensajes:
            texto = mensaje.css(".tgme_widget_message_text *::text").getall()
            texto_completo = ''.join(texto)
            
            fecha_completa = mensaje.css("time::attr(datetime)").get()
            
            if fecha_completa:
                fecha_utc = datetime.fromisoformat(fecha_completa.replace('Z', '+00:00'))  # Convertir UTC
                fecha_local = fecha_utc.astimezone(tz_ny)
                
                hora = fecha_local.strftime("%H:%M")
                dia = fecha_local.strftime("%Y-%m-%d")
                
                if fecha_local.strftime("%Y-%m-%d") == hoy and all(filtro in texto_completo.lower() for filtro in filtros):
                    self.resultados.append({
                        "dia": dia,
                        "hora": hora,
                        "texto": texto_completo,
                    })

def ejecutar_spider():
    # Instanciar la spider
    spider = TelegramSpider

    process = CrawlerProcess(settings={
        'LOG_LEVEL': 'INFO',
    })

    # Ejecutar la spider
    process.crawl(spider)
    process.start()

    return spider.resultados

# if __name__ == "__main__":
#     datos = ejecutar_spider()
#     print("Resultados obtenidos:")
#     for item in datos:
#         print(item)