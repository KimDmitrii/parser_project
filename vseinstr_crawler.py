import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import cloudscraper #без него этот сайт у меня не получилось обработать
import csv
import sys
import pandas as pd

sys.setrecursionlimit(5000) # очень много ссылок, если скрапить весь каталог


pages = set()
scraper = cloudscraper.CloudScraper()
session = requests.Session()
headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)'
           'AppleWebKit 537.36 (KHTML, like Gecko) Chrome',
           'Accept':'text/html,application/xhtml+xml,application/xml;'
           'q=0.9,image/webp,*/*;q=0.8'}

list_of_content = ['instrument',
                   'ofis-i-dom']
                #    'sadovaya_tehnika', 
                #    'ruchnoy-instrument', 
                #    'electrika_i_svet',
                #    'klimat', 
                #    'krepezh', 
                #    'skladskoe-oborudovanie', 
                #    'stanki', 
                #    'rashodnie_materialy', 
                #    'stroitelnye-materialy',
                #    'uborka', 
                #    'otdyh-i-sport', 
                #    'spetsodezhda']

data = []

def getData(pageUrl):
    global pages, list_of_content
    for s in list_of_content: 
        html = 'https://rostov.vseinstrumenti.ru/'.format(pageUrl) + s
        req = scraper.get(html, headers=headers)
        bs = BeautifulSoup(req.text, 'lxml')
        try:
            for link in bs.find_all('a', href=re.compile('^(/{}/)((?!:).)*$'.format(s))):
                if link.attrs['href'] not in pages:
                    new_html = 'https://rostov.vseinstrumenti.ru' + link.attrs['href']
                    req2 = scraper.get(new_html, headers=headers)
                    bs2 = BeautifulSoup(req2.text, 'lxml')
                    try:
                        count = bs2.find('div', {'pagination'}).get('data-max-page').strip()
                        print(count)
                        unit = bs2.find('span', {'current'})
                        for i in range(2, int(count)):
                            html2 = 'https://rostov.vseinstrumenti.ru' + link.attrs['href'] + 'page{}/#goods'.format(i)
                            req3 = scraper.get(html2, headers=headers)
                            bs3 = BeautifulSoup(req3.text, 'lxml')
                            product2 = bs3.find_all('div', {'product-tile grid-item'})
                            for p2 in product2:
                                try:
                                    price = p2.find('div', {'class':'price'}).find('span').text.strip()
                                except AttributeError:
                                    price = 'N/A'
                                    continue
                                try:
                                    id = p2.find('div', {'class':'wtis-id'}).find('span').text.strip()
                                except AttributeError:
                                    id = 'None'
                                    continue
                                try:
                                    name = p2.find('a', {'data-behavior':'product-name'}).get('title').strip()
                                except AttributeError:
                                    name = 'X'
                                    continue
                                product_data = {'price': price, 'id': id, 'name': name, 'link': link.attrs['href'], 'unit': unit.text}
                                data.append(product_data)
                            newPage = link.attrs['href']
                            print(html2)
                            pages.add(newPage)
                            
                    except AttributeError:
                        print('pagination hasn"t found')
                        continue

                    new_html = 'https://rostov.vseinstrumenti.ru' + link.attrs['href']
                    req2 = scraper.get(new_html, headers=headers)
                    bs2 = BeautifulSoup(req2.text, 'lxml')
                    product = bs2.find_all('div', {'product-tile grid-item'})
                    unit = bs2.find('span', {'current'})
                    for p in product:
                        try:
                            price = p.find('div', {'class':'price'}).find('span').text.strip()
                        except AttributeError:
                            price = 'N/A'
                            continue
                        try:
                            id = p.find('div', {'class':'wtis-id'}).find('span').text.strip()
                        except AttributeError:
                            id = 'None'
                            continue
                        try:
                            name = p.find('a', {'data-behavior':'product-name'}).get('title').strip()
                        except AttributeError:
                            name = 'X'
                            continue
                        product_data = {'price': price, 'id': id, 'name': name, 'link': link.attrs['href'], 'unit': unit.text}
                        data.append(product_data)

                    newPage = link.attrs['href']
                    print(new_html)
                    pages.add(newPage)
        except requests.exceptions.ChunkedEncodingError as ex:

            print(f"Invalid chunk encoding {str(ex)}")

getData('')


with open('vse.csv', 'wt+', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=';')        
    for product in data:
        writer.writerow((product['unit'], product['name'], product['id'], product['price'], product['link']))

# https://rostov.vseinstrumenti.ru/instrument/
# https://rostov.vseinstrumenti.ru/ofis-i-dom
# https://rostov.vseinstrumenti.ru/sadovaya_tehnika
# https://rostov.vseinstrumenti.ru/ruchnoy-instrument/
# https://rostov.vseinstrumenti.ru/electrika_i_svet/
# https://rostov.vseinstrumenti.ru/klimat/
# https://rostov.vseinstrumenti.ru/krepezh/
# https://rostov.vseinstrumenti.ru/skladskoe-oborudovanie/
# https://rostov.vseinstrumenti.ru/stanki/
# https://rostov.vseinstrumenti.ru/rashodnie_materialy/
# https://rostov.vseinstrumenti.ru/stroitelnye-materialy/
# https://rostov.vseinstrumenti.ru/uborka/
# https://rostov.vseinstrumenti.ru/otdyh-i-sport/
# https://rostov.vseinstrumenti.ru/spetsodezhda/

# ТЕХНОНИКОЛЬ - https://rostov-na-donu.tstn.ru/shop/
# Краски.ру - https://rostov.kraski.ru/
# 220вольт - https://rostov.220-volt.ru/
# вашдом - https://vashdom24.ru/
# строитель_батайск - https://stroitel-btsk.ru/