import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
# import cloudscraper
import csv
import sys

sys.setrecursionlimit(5000)


# pages = set()
# scraper = cloudscraper.CloudScraper()
session = requests.Session()
headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)'
           'AppleWebKit 537.36 (KHTML, like Gecko) Chrome',
           'Accept':'text/html,application/xhtml+xml,application/xml;'
           'q=0.9,image/webp,*/*;q=0.8'}

list_of_content = [
    'sukhie_stroitelnye_smesi',
    'otdelochnye_materialy']
    # 'lakokrasochnye_materialy',
#     'instrumenty_oborudovanie',
#     'raskhodnye_materialy',
#     'krepezh',
#     'zamochno_skobyanye_izdeliya',
#     'inzhenernye_sistemy',
#     'santekhnika',
#     'osveshchenie',
#     'elektrotovary',
#     'tovary_dlya_doma_i_sada'
# ]

# ['lakokrasochnye_materialy', 'instrumenty_oborudovanie']



data = []

def getData():
    global pages, list_of_content
    for s in list_of_content:
        html = 'https://vashdom24.ru/catalog/' + s
        req = session.get(html, headers=headers)
        bs = BeautifulSoup(req.text, 'html.parser')
        conteiners = bs.find_all('div', {'class': 'col-6 col-sm-6 col-md-4 col-lg-3 col-xl-2 my-3'})
        for conteiner in conteiners:
            link = conteiner.find('a')    
            html = 'https://vashdom24.ru' + link.attrs['href']
            req = session.get(html, headers=headers)
            bs = BeautifulSoup(req.text, 'html.parser')
            number_of_pages = bs.find_all('a', {'data-pagen': '1'})
            product = bs.find_all('div', {'class': 'row product-item'})
            unit = bs.find('li', {'class': 'uk-active'}).find('span', {'itemprop':'title'}).text
            for p in product:
                try:
                    price = p.find('span', {'class': 'b-product-item__price'}).text.strip()
                    # print(price)
                except AttributeError:
                    price = 'N/A'
                    continue
                try:
                    id = p.find('div', {'class': 'b-product-item__code b-product-item__code--line pb-3 pb-lg-0'}).text[12:].strip()
                    # print(id)
                except AttributeError:
                    id = 'None'
                    continue
                try:
                    name = p.find('div', {'class':'b-product-item__name pb-2'}).text.strip()
                except AttributeError:
                    name = 'X'
                    continue
                product_data = {'id': id, 'name': name, 'price': price, 'link': link.attrs['href'], 'unit': unit}
                data.append(product_data)
            
            if number_of_pages:
                max_page = int(number_of_pages[-3].text)
                for number in range(2, max_page):
                    html2 = 'https://vashdom24.ru' + link.attrs['href'] + '?PAGEN_1={}'.format(number)
                    req2 = session.get(html2, headers=headers)
                    bs2 = BeautifulSoup(req2.text, 'html.parser')
                    product = bs2.find_all('div', {'class': 'row product-item'})
                    unit = bs2.find('li', {'class': 'uk-active'}).find('span', {'itemprop':'title'}).text
                    for p in product:
                        try:
                            price = p.find('span', {'class': 'b-product-item__price'}).text.strip()
                            # print(price)
                        except AttributeError:
                            price = 'N/A'
                            continue
                        try:
                            id = p.find('div', {'class': 'b-product-item__code b-product-item__code--line pb-3 pb-lg-0'}).text[12:].strip()
                            # print(id)
                        except AttributeError:
                            id = 'None'
                            continue
                        try:
                            name = p.find('div', {'class':'b-product-item__name pb-2'}).text.strip()
                        except AttributeError:
                            name = 'X'
                            continue
                        product_data = {'id': id, 'name': name, 'price': price, 'link': link.attrs['href'], 'unit': unit}
                        data.append(product_data)
                    newPage = link.attrs['href']
                    print(html2)
                    # pages.add(newPage)

            newPage = link.attrs['href']
            print(html)
            # pages.add(newPage)

getData()

with open('vashdom.csv', 'wt+', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=';')        
    for product in data:
        writer.writerow((product['unit'], product['name'], product['id'], product['price'], product['link']))

# <div class="b-product-item__code b-product-item__code--line pb-3 pb-lg-0"><span class="">Код товара:</span> 26993<br></div>