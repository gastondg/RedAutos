import requests
from lxml.html import fromstring
from itertools import cycle
import traceback

class Proxies:

    def scrap_proxies(self):
        url = 'https://free-proxy-list.net/'
        response = requests.get(url)
        parser = fromstring(response.text)
        proxies = set()
        for i in parser.xpath('//tbody/tr')[:10]:
            if i.xpath('.//td[7][contains(text(),"yes")]'):
                #Grabbing IP and corresponding PORT
                proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
                proxies.add(proxy)
        validados = self.validate_proxies(proxies)
        return validados

    def get_proxies(self):
        proxies = self.scrap_proxies()
        #proxy_pool = cycle(proxies)
        proxy_json = [{"http": proxy, "https": proxy} for proxy in proxies]
        return proxy_json

    def validate_proxies(self, proxies):
        validados = set()
        url = 'https://httpbin.org/ip'
        for proxy in proxies:
            try:
                proxy_sinport = str(proxy.split(":")[0])
                
                print("Validando proxy con ip:",proxy)
                
                response = requests.get(url,proxies={"http": proxy, "https": proxy})
                response_json = response.json()
                
                print("Response: ",str(response_json))
                
                ip_response = response_json["origin"].split(",")[0].strip()
                
                print("Ip de la respuesta:", ip_response)
                
                if proxy_sinport == ip_response:
                    validados.add(proxy)
                    print(True)
            
            except Exception as e:
                #Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work. 
                #We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url 
                print("Skipping. Connnection error")
                print(e)
        return validados

if __name__ == "__main__":
    proxClass = Proxies()
    proxies = proxClass.get_proxies()
    print(proxies)

    """ proxies = get_proxies()
    proxy_pool = cycle(proxies)
    print("Esto es cycle proxies")
    print(proxy_pool)

    url = 'https://httpbin.org/ip'
    for i in range(1,11):
        #Get a proxy from the pool
        proxy = next(proxy_pool)
        print("Request #%d"%i)
        try:
            response = requests.get(url,proxies={"http": proxy, "https": proxy})
            print(response.json())
        except:
            #Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work. 
            #We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url 
            print("Skipping. Connnection error") """