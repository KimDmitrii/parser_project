from __future__ import absolute_import, unicode_literals
import requests
from bs4 import BeautifulSoup
import json
from celery import app, shared_task
from .models import Data
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

pages = set()
session = requests.Session()
headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)'
           'AppleWebKit 537.36 (HTML, like Gecko) Chrome',
           'Accept':'text/html,application/xhtml+xml,application/xml;'
           'q=0.9,image/webp,*/*;q=0.8'}

data1 = []


@shared_task(serializer='json')
def getLinksFromPagination():
    global pages
    html = 'https://stroitel-btsk.ru/'
    req = session.get(html, headers=headers)
    bs = BeautifulSoup(req.text, 'html.parser')
    catalog = bs.find('div', {'class': 'col-12 col-lg-3 order-lg-1'})
    links = catalog.find_all('a')
    for link in links:
        html2 = 'https://stroitel-btsk.ru/' + link.attrs['href']
        req2 = session.get(html2, headers=headers)
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
                price_t = p.find('div', {'class': 'price'}).find('b').text.strip()
                price = float(price_t.replace(' ', ''))
                product_data = {'id': id,
                                'name': name,
                                'price': price,
                                'unit': unit.text,
                                'link': link.attrs['href'],
                                'site': 'stroitel'}
                data1.append(product_data)

        if len(last_page) > 0:
            print(last_page[-1].attrs['href'][-1])
            count = last_page[-1].attrs['href'][-1]
            for i in range(2, int(count) + 1):
                html3 = 'https://stroitel-btsk.ru/' + link.attrs['href'] + '?page={}'.format(i)
                req3 = session.get(html3, headers=headers)
                bs3 = BeautifulSoup(req3.text, 'html.parser')
                product2 = bs3.find_all('div', {'class': 'product'})
                for p in product2:
                    section = bs3.find_all('span', {'itemprop': 'name'})
                    unit = section[-1]
                    name = p.find('span', {'class': 'title'}).text.strip()
                    id = p.find('div', {'class': 'article'}).text.strip()
                    price_t = p.find('div', {'class': 'price'}).find('b').text.strip()
                    price = float(price_t.replace(' ', ''))
                    product_data = {'id': id,
                                    'name': name,
                                    'price': price,
                                    'unit': unit.text,
                                    'link': link.attrs['href'],
                                    'site': 'stroitel'}
                    data1.append(product_data)
                print(html3)
        print(html2)
    print(html)
    return save_function(data1)


@shared_task(serializer='json')
def save_function(data):
    new_count = 0
    for product_data in data:
        try:
            Data.objects.update_or_create(
                category=product_data['unit'],
                name=product_data['name'],
                id=product_data['id'],
                price=product_data['price'],
                link=product_data['link'],
                site=product_data['site']
            )
            new_count += 1
        except Exception as e:
            print('failed at latest_product_data in none')
            print(e)
            break
    return print('finished')
