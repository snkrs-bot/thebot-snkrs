import scrapy,random
import json
from datetime import datetime
try:
    from crawler.crawler.items import Inserter,  Deleter
except:
    from crawler.items import Inserter,  Deleter

class GdlpRestockSpider(scrapy.Spider):
    name = "gdlp_restock"
    encontrados = {}   
    def __init__(self, results, proxy_list=None):  
        self.proxy_pool = proxy_list
        self.encontrados[self.name] = []      
        [self.add_name(self.name, str(r['id']))  for r in results if r['spider'] == self.name]
        self.first_time = len(self.encontrados[self.name])
        
    def make_request(self, url, cb, meta=None, handle_failure=None):
        request = scrapy.Request(dont_filter=True, url =url, callback=cb, meta=meta, errback=handle_failure)
        if self.proxy_pool:
            request.meta['proxy'] = random.choice(self.proxy_pool)              
            # self.log('Using proxy {}'.format(request.meta['proxy']))          
            # self.log('----------------')
        return request 

    def detail_failure(self, failure):        
        record = Inserter()
        record = failure.request.meta['record']
        # try with a new proxy
        self.log('Erro em detalhes url {}'.format(failure.request.url))
        self.log('Erro em detalhes url {}'.format(failure.request.url))
        self.log('Erro em detalhes url {}'.format(failure.request.url))
        self.log('Erro em detalhes url {}'.format(failure.request.url))
        self.log('Erro em detalhes url {}'.format(failure.request.url))
        self.log('Erro em detalhes url {}'.format(failure.request.url))
        self.log('Erro em detalhes url {}'.format(failure.request.url))
        request = self.make_request(failure.request.url, self.details, dict(record=record), self.detail_failure)
        yield request 

    def page_failure(self, failure):        
        # try with a new proxy
        self.log('**** Erro em PAGINACAO url {}'.format(failure.request.url))
        self.log('**** Erro em PAGINACAO url {}'.format(failure.request.url))
        self.log('**** Erro em PAGINACAO url {}'.format(failure.request.url))
        self.log('**** Erro em PAGINACAO url {}'.format(failure.request.url))
        self.log('**** Erro em PAGINACAO url {}'.format(failure.request.url))
        self.log('**** Erro em PAGINACAO url {}'.format(failure.request.url))
        self.log('**** Erro em PAGINACAO url {}'.format(failure.request.url))

        request = self.make_request(failure.request.url, self.parse, None, self.page_failure)
        yield request

    def start_requests(self): 
        urls = [            
            'https://gdlp.com.br/calcados/adidas',
            'https://gdlp.com.br/calcados/nike',
            'https://gdlp.com.br/calcados/air-jordan',
            'https://gdlp.com.br/calcados/new-balance'
        ]
        for url in urls:
            request = self.make_request(url, self.parse, None, self.page_failure)            
            yield request 
            #yield scrapy.Request(dont_filter=True, url =url, callback=self.parse)  
       
    def add_name(self, key, id):
        if key in  self.encontrados:
            self.encontrados[key].append(id)
        else:
            self.encontrados[key] = [id]

    def parse(self, response):     
        finish  = True
        tab = response.url.replace('?','/').split('/')[4]  
        categoria = 'gdlp_restock' 
        
        send = 'avisar' if int(self.first_time) > 0 else 'avisado'

        #pega todos os ites da pagina, apenas os nomes dos tenis
        nodes = [ name for name in response.xpath('//li[@class="item last"]') ]
        if(len(nodes) > 0 ):
            finish=False
      
        #checa se o que esta na pagina ainda nao esta no banco, nesse caso insere com o status de avisar
        for item in nodes: 
            name = item.xpath('.//h2//a/text()').get()
            prod_url = item.xpath('.//a/@href').get()
            id_price = item.xpath('.//span[@class="regular-price"]/@id').get()           
            id = 'ID{}-{}$'.format(id_price.split('-')[-1].split('_')[0], tab)
            price = item.xpath('.//span[@class="price"]/text()').get()
            deleter = Deleter()                      
            deleter['id']=id
            yield deleter
            record = Inserter()
            record['id']=id 
            record['created_at']=datetime.now().strftime('%Y-%m-%d %H:%M') 
            record['spider']=self.name 
            record['codigo']=id_price.split('-')[-1].split('_')[0] 
            record['prod_url']=prod_url 
            record['name']=name 
            record['categoria']=categoria 
            record['tab']=tab 
            record['send']=send      
            record['imagens']=''  
            record['tamanhos']=''    
            record['price']=price          
            record['outros']=''      
            if len( [id_db for id_db in self.encontrados[self.name] if str(id_db) == str(id)]) == 0:     
                self.add_name(self.name, str(id))
                request = self.make_request(prod_url, self.details, dict(record=record), self.detail_failure)            
                yield request
                #yield scrapy.Request(dont_filter=True, url =prod_url, callback=self.details,  meta=(dict(record=record)))
        
        if(finish == False):
            paginacao = response.xpath('//div[@class="pages"]//li')
            if len(paginacao) > 0:
                url = response.xpath('//div[@class="pages"]//a[@class="next i-next"]/@href').get()
                if url:                
                    yield scrapy.Request(dont_filter=True, url =url, callback=self.parse)

    def details(self, response):   
        record = Inserter()
        record = response.meta['record']       
        opcoes_list = []
        images_list = []
        images = response.xpath('//div[@class="product-img-box"]//a/@data-image').getall()
        for imagem in images:
            images_list.append(imagem)        
        items = response.xpath('//script/text()').getall()  
        price = response.xpath('//span[@class="price"]/text()').get()        
        for item in items:   
            if('new Product.Config(' in item):                
                tamanhos = item.split('(')[1].split(');')[0].strip()                                
                options = json.loads(tamanhos)['attributes']                
                for k in options.keys():
                    for option in options[k]['options']:
                        if len(option['products']) > 0:
                            opcoes_list.append({'tamanho' : option['label']})
        record['price']=price
        record['prod_url']=response.url 
        record['imagens']="|".join(images_list) 
        record['tamanhos']=json.dumps(opcoes_list)
        yield record    

      
        


        