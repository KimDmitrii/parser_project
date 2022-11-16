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

list_of_content = ['llakokrasochnyie-materialyi', 'tovaryi-dlya-doma-i-sada']

# [
#     'sukhie_stroitelnye_smesi',
#     'otdelochnye_materialy',
#     'lakokrasochnye_materialy',
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

data = []

def getData():
    global pages, list_of_content
    html = 'https://stroitel-btsk.ru/'
    req = session.get(html, headers=headers)
    bs = BeautifulSoup(req.text, 'html.parser')
    catalog = bs.find('div', {'class': 'col-12 col-lg-3 order-lg-1'})
    links = catalog.find_all('a')
    for link in links:
        html2 = 'https://stroitel-btsk.ru/' + link.attrs['href']
        req2 =  session.get(html2, headers=headers)
        bs2 = BeautifulSoup(req2.text, 'html.parser')
        product = bs2.find_all('div', {'class': 'product'})
        last_page = bs2.find_all('a', {'class': 'page-link'})
        # print(len(product))
        if len(product) > 0:
            for p in product:
                section = bs2.find_all('span', {'itemprop': 'name'})
                unit = section[-1]
                name = p.find('span', {'class': 'title'}).text.strip()
                id = p.find('div', {'class': 'article'}).text.strip()
                price = p.find('div', {'class': 'price'}).find('b').text.strip()
                product_data = {'id': id, 'name': name, 'price': price, 'unit': unit.text, 'link': link.attrs['href']}
                data.append(product_data)

        if len(last_page) > 0:
            print(last_page[-1].attrs['href'][-1])
            count = last_page[-1].attrs['href'][-1]
            for i in range(2, int(count) + 1):
                html3 = 'https://stroitel-btsk.ru/' + link.attrs['href'] + '?page={}'.format(i)
                req3 =  session.get(html3, headers=headers)
                bs3 = BeautifulSoup(req3.text, 'html.parser')
                product2 = bs3.find_all('div', {'class': 'product'})
                for p in product2:
                    section = bs3.find_all('span', {'itemprop': 'name'})
                    unit = section[-1]
                    name = p.find('span', {'class': 'title'}).text.strip()
                    id = p.find('div', {'class': 'article'}).text.strip()
                    price = p.find('div', {'class': 'price'}).find('b').text.strip()
                    product_data = {'id': id, 'name': name, 'price': price,'unit': unit.text, 'link': link.attrs['href']}
                    data.append(product_data)
                print(html3)
        print(html2)
    print(html)


getData()

with open('stroitel_btsk.csv', 'wt+', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=';')        
    for product in data:
        writer.writerow((product['unit'], product['name'], product['id'], product['price'], product['link']))
