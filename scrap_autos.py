import string
import random
import requests
from lxml.html import fromstring
from itertools import cycle
import traceback

def scrap_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies
        
def get_proxies():
    proxies = scrap_proxies()
    #proxy_pool = cycle(proxies)
    proxy_json = [{"http": proxy, "https": proxy} for proxy in proxies]
    return proxy_json

def patente_generator(cuantas=50):
    patentes = set()
    for i in range(cuantas):
        caracteres = ''.join(random.choice(string.ascii_uppercase) for _ in range(3))
        numeros = ''.join(random.choice(string.digits) for _ in range(3))
        patentes.add(caracteres+numeros)
    return patentes

def get_datos_patente(patente):
    """La patente es tipo string"""
    url = "https://cetaweb.afip.gob.ar/api/v1/automotor?dominio={}"

    # DEBERÍAMOS TENER UN TRY ACÁ DE SCRAP
    # SIN PROXIES

    proxies = get_proxies()
    for proxy in proxies:
        try:
            proxy = random.choice(proxies)
            print(proxy)
            response = requests.get(url.format(patente),proxies=proxy)
            json = response.json()
            print(json)
            if json['p_aut_fmm_ds'] != None:
                # GUARDAR EN BASE DE DATOS
                print("Guardando en base de datos")
                break
        except:
            print("Hubo un problema")
    return

if __name__ == "__main__":
    get_datos_patente("HBC387")
    """ patentes = patente_generator()
    proxies = get_proxies()
    url = "https://cetaweb.afip.gob.ar/api/v1/automotor?dominio={}"
    for patente in patentes:
        try:
            proxy = random.choice(proxies)
            print(proxy)
            response = requests.get(url.format(patente),proxies=proxy)
            print(response.json())
        except Exception as e:
            print("Hubo un problema")
            print(e)
 """