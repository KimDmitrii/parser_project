from __future__ import absolute_import, unicode_literals
import requests
from bs4 import BeautifulSoup
import json
from celery import app, shared_task
from .models import Data
from celery.utils.log import get_task_logger
import time
import cloudscraper

logger = get_task_logger(__name__)

session = requests.Session()
scraper = cloudscraper.CloudScraper()
headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)'
           'AppleWebKit 537.36 (HTML, like Gecko) Chrome',
           'Accept':'text/html,application/xhtml+xml,application/xml;'
           'q=0.9,image/webp,*/*;q=0.8'}

data1 = []
pages = set()

@shared_task(serializer='json')
def get_datastroitel():
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
                product_id = p.find('div', {'class': 'article'}).text.strip()
                price_t = p.find('div', {'class': 'price'}).find('b').text.strip()
                price = float(price_t.replace(' ', ''))
                product_data = {
                    'product_id': product_id,
                    'name': name,
                    'price': price,
                    'unit': unit.text,
                    'link': link.attrs['href'],
                    'site': 'stroitel'
                }
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
                    product_id = p.find('div', {'class': 'article'}).text.strip()
                    price_t = p.find('div', {'class': 'price'}).find('b').text.strip()
                    price = float(price_t.replace(' ', ''))
                    product_data = {
                        'product_id': product_id,
                        'name': name,
                        'price': price,
                        'unit': unit.text,
                        'link': link.attrs['href'],
                        'site': 'stroitel'
                    }
                    data1.append(product_data)
                print(html3)
        print(html2)
    print(html)
    return get_data_vseinstrumenti()


@shared_task(serializer='json')
def get_data_vseinstrumenti():
    html = 'https://rostov.vseinstrumenti.ru/map.html'
    req = scraper.get(html, headers=headers)
    bs = BeautifulSoup(req.text, 'lxml')
    for link in bs.find_all('a', {'class': 'catalog-link'}):
        if link.attrs['href'] not in pages:
            catalog_html = 'https://rostov.vseinstrumenti.ru' + link.attrs['href']
            try:
                req2 = scraper.get(catalog_html, headers=headers, verify=False)
            except requests.ConnectionError as e:
                print("Connection Error.\n")
                print(str(e))
                continue
            bs2 = BeautifulSoup(req2.text, 'lxml')
            try:
                count = bs2.find('div', {'pagination'}).get('data-max-page').strip()
                unit = bs2.find('span', {'current'})
                if count:
                    print(count)
                    for i in range(2, int(count)):
                        page_html = 'https://rostov.vseinstrumenti.ru' + link.attrs['href'] + 'page{}/#goods'.format(i)
                        req3 = scraper.get(page_html, headers=headers, verify=False)
                        bs3 = BeautifulSoup(req3.text, 'lxml')
                        product2 = bs3.find_all('div', {'product-tile grid-item'})
                        for p2 in product2:
                            try:
                                price = p2.find('div', {'class':'price'}).find('span').text.strip()
                            except AttributeError:
                                print(f'there is no price in {page_html}')
                                price = 0
                            product_id = p2.find('div', {'class':'wtis-id'}).find('span').text.strip()
                            name = p2.find('a', {'data-behavior':'product-name'}).get('title').strip()
                            product_data = {
                                'price': price,
                                'product_id': product_id,
                                'name': name,
                                'link': link.attrs['href'],
                                'unit': unit.text,
                                'site': 'vseinstrumenti'
                            }
                            data1.append(product_data)
                        print(page_html)
                        pages.add(link.attrs['href'])
            except AttributeError:
                print(f"{catalog_html} has no pagination" )
                continue

            product = bs2.find_all('div', {'product-tile grid-item'})
            for p in product:
                try:
                    price = p.find('div', {'class':'price'}).find('span').text.strip()
                except AttributeError:
                    print(f'there is no price in {page_html}')
                product_id = p.find('div', {'class':'wtis-id'}).find('span').text.strip()
                name = p.find('a', {'data-behavior':'product-name'}).get('title').strip()
                product_data = {
                    'price': price,
                    'product_id': product_id,
                    'name': name,
                    'link': link.attrs['href'],
                    'unit': unit.text,
                    'site': 'vseinstrumenti'
                }
                data1.append(product_data)
            print(catalog_html)


@shared_task(serializer='json')
def get_data_vasdom():
    html = 'https://vashdom24.ru/catalog/'
    req = session.get(html, headers=headers)
    bs = BeautifulSoup(req.text, 'html.parser')
    containers = bs.find_all('li', {'class': 'catalog-categories-lvl2__li'})
    for container in containers:
        link = container.find('a')
        html = 'https://vashdom24.ru' + link.attrs['href']
        req = session.get(html, headers=headers)
        bs = BeautifulSoup(req.text, 'html.parser')
        number_of_pages = bs.find_all('a', {'data-pagen': '1'})
        product = bs.find_all('div', {'class': 'row product-item'})
        unit = bs.find('li', {'class': 'uk-active'}).find('span', {'itemprop': 'title'}).text
        for p in product:
            try:
                price = p.find('span', {'class': 'b-product-item__price'}).text.strip()
                # print(price)
            except AttributeError:
                price = 'N/A'
                continue
            try:
                product_id = p.find('div', {'class': 'b-product-item__code b-product-item__code--line pb-3 pb-lg-0'}).text.strip()
                # print(id)
            except AttributeError:
                id = 'None'
                continue
            try:
                name = p.find('div', {'class': 'b-product-item__name pb-2'}).text.strip()
            except AttributeError:
                name = 'X'
                continue
            product_data = {
                'product_id': product_id,
                'name': name, 'price': price,
                'link': link.attrs['href'],
                'unit': unit,
                'site': 'vashdom'
            }
            data1.append(product_data)

        if number_of_pages:
            max_page = int(number_of_pages[-3].text)
            for number in range(2, max_page):
                html2 = 'https://vashdom24.ru' + link.attrs['href'] + '?PAGEN_1={}'.format(number)
                req2 = session.get(html2, headers=headers)
                bs2 = BeautifulSoup(req2.text, 'html.parser')
                product = bs2.find_all('div', {'class': 'row product-item'})
                unit = bs2.find('li', {'class': 'uk-active'}).find('span', {'itemprop': 'title'}).text
                for p in product:
                    try:
                        price = p.find('span', {'class': 'b-product-item__price'}).text.strip()
                        # print(price)
                    except AttributeError:
                        price = 'N/A'
                        continue
                    try:
                        product_id = p.find('div',
                                    {'class': 'b-product-item__code b-product-item__code--line pb-3 pb-lg-0'}).text.strip()
                        # print(id)
                    except AttributeError:
                        product_id = 'None'
                        continue
                    try:
                        name = p.find('div', {'class': 'b-product-item__name pb-2'}).text.strip()
                    except AttributeError:
                        name = 'X'
                        continue
                    product_data = {
                        'product_id': product_id,
                        'name': name,
                        'price': price,
                        'link': link.attrs['href'],
                        'unit': unit,
                        'site': 'vashdom'
                    }
                    data1.append(product_data)
                print(html2)
        print(html)
    return get_data_stroymir()

@shared_task(serializer='json')
def get_data_stroymir():
    html = 'https://rnd.4stm.ru/index.php?route=product/category/catalog'
    req = session.get(html, headers=headers)

    bs = BeautifulSoup(req.text, 'html.parser')
    container = bs.find('div', {'id': 'categorybase'})
    links = container.find_all('a')
    # Основные ссылки из каталога
    for l in links:
        category_link = l.attrs['href']
        try:
            req2 = session.get(category_link, headers=headers)
        except ConnectionError as e:
            print(e)
            continue
        bs2 = BeautifulSoup(req2.text, 'html.parser')
        category_containers = bs2.find_all('div', {'class': 'good good-category'})
        products = bs2.find_all('div', {'class': 'good-title'})
        # Если найдены карточки товара, то начинаем их скрапить
        if products:
            pagination = bs2.find('div', {'class': 'results'}).text
            last_page = int(pagination[-3])
            for product in products:
                product_link = product.find('a').attrs['href']
                try:
                    req3 = session.get(product_link, headers=headers)
                except ConnectionError as e:
                    print(e)
                    continue
                bs3 = BeautifulSoup(req3.text, 'html.parser')
                price_td = bs3.find_all('td')[-3]
                price = float(price_td.text.strip().replace(',', '.'))
                product_id = bs3.find('div', {'class': 'pcard-model'}).text.strip()
                name = bs3.find('div', {'class': 'pcard-name'}).text.strip()
                unit = bs3.find_all('span', {'class': 'el'})[-2]
                product_data = {
                    'product_id': product_id,
                    'name': name,
                    'price': price,
                    'link': product_link,
                    'unit': unit.text.strip(),
                    'site': 'stroymir'
                }
                data1.append(product_data)

            # Проверка наличия пагинации
            if last_page > 1:
                for page in range(2, last_page):
                    category_link_page = product_link + '?page={}'.format(page)
                    try:
                        req_page = session.get(category_link_page, headers=headers)
                    except ConnectionError as e:
                        print(e)
                        continue
                    bs_page = BeautifulSoup(req_page.text, 'html.parser')
                    products = bs_page.find_all('div', {'class': 'good-title'})
                    for product in products:
                        product_link = product.find('a').attrs['href']
                        try:
                            req3 = session.get(product_link, headers=headers)
                        except ConnectionError as e:
                            print(e)
                            continue
                        bs3 = BeautifulSoup(req3.text, 'html.parser')
                        price_td = bs3.find_all('td')[-3]
                        price = float(price_td.text.strip().replace(',', '.'))
                        product_id = bs3.find('div', {'class': 'pcard-model'}).text.strip()
                        name = bs3.find('div', {'class': 'pcard-name'}).text.strip()
                        unit = bs3.find_all('span', {'class': 'el'})[-2]
                        product_data = {
                            'product_id': product_id,
                            'name': name,
                            'price': price,
                            'link': product_link,
                            'unit': unit.text.strip(),
                            'site': 'stroymir'
                        }
                        data1.append(product_data)
                    print(category_link_page)

        # Карточки товара не найдены, проходимся по второму уровню каталожных ссылок
        else:
            for category_container in category_containers:
                category_link2 = category_container.find('a').attrs['href']
                try:
                    req4 = session.get(category_link2, headers=headers)
                except ConnectionError as e:
                    print(e)
                    continue
                bs4 = BeautifulSoup(req4.text, 'html.parser')
                category_containers2 = bs4.find_all('div', {'class': 'good good-category'})
                products = bs4.find_all('div', {'class': 'good-title'})

                # Если найдены карточки товара, то начинаем их скрапить
                if products:
                    pagination = bs4.find('div', {'class': 'results'}).text
                    last_page = int(pagination[-3])
                    for product in products:
                        product_link = product.find('a').attrs['href']
                        try:
                            req3 = session.get(product_link, headers=headers)
                        except ConnectionError as e:
                            print(e)
                            continue
                        bs3 = BeautifulSoup(req3.text, 'html.parser')
                        price_td = bs3.find_all('td')[-3]
                        price = float(price_td.text.strip().replace(',', '.'))
                        product_id = bs3.find('div', {'class': 'pcard-model'}).text.strip()
                        name = bs3.find('div', {'class': 'pcard-name'}).text.strip()
                        unit = bs3.find_all('span', {'class': 'el'})[-2]
                        print(unit.text.strip())
                        product_data = {
                            'product_id': product_id,
                            'name': name,
                            'price': price,
                            'link': product_link,
                            'unit': unit.text.strip(),
                            'site': 'stroymir'
                        }
                        data1.append(product_data)
                        print(product_link)

                    # Проверка наличия пагинации
                    if last_page > 1:
                        for page in range(2, last_page):
                            category_link_page = product_link + '?page={}'.format(page)
                            try:
                                req_page = session.get(category_link_page, headers=headers)
                            except ConnectionError as e:
                                print(e)
                                continue
                            bs_page = BeautifulSoup(req_page.text, 'html.parser')
                            products = bs_page.find_all('div', {'class': 'good-title'})
                            for product in products:
                                product_link = product.find('a').attrs['href']
                                try:
                                    req3 = session.get(product_link, headers=headers)
                                except ConnectionError as e:
                                    print(e)
                                    continue
                                bs3 = BeautifulSoup(req3.text, 'html.parser')
                                price_td = bs3.find_all('td')[-3]
                                price = float(price_td.text.strip().replace(',', '.'))
                                product_id = bs3.find('div', {'class': 'pcard-model'}).text.strip()
                                name = bs3.find('div', {'class': 'pcard-name'}).text.strip()
                                unit = bs3.find_all('span', {'class': 'el'})[-2]
                                product_data = {
                                    'product_id': product_id,
                                    'name': name,
                                    'price': price,
                                    'link': product_link,
                                    'unit': unit.text.strip(),
                                    'site': 'stroymir'
                                }
                                data1.append(product_data)
                                print(product_link)
                            print(category_link_page)

                # переходим на третий(последний) уровень каталожных ссылок
                else:
                    for category_container in category_containers2:
                        category_link2 = category_container.find('a').attrs['href']
                        try:
                            req4 = session.get(category_link2, headers=headers)
                        except ConnectionError as e:
                            print(e)
                            continue
                        bs4 = BeautifulSoup(req4.text, 'html.parser')
                        products = bs4.find_all('div', {'class': 'good-title'})
                        if products:
                            pagination = bs4.find('div', {'class': 'results'}).text
                            last_page = int(pagination[-3])
                            for product in products:
                                product_link = product.find('a').attrs['href']
                                try:
                                    req3 = session.get(product_link, headers=headers)
                                except ConnectionError as e:
                                    print(e)
                                    continue
                                bs3 = BeautifulSoup(req3.text, 'html.parser')
                                price_td = bs3.find_all('td')[-3]
                                price = float(price_td.text.strip().replace(',', '.'))
                                product_id = bs3.find('div', {'class': 'pcard-model'}).text.strip()
                                name = bs3.find('div', {'class': 'pcard-name'}).text.strip()
                                unit = bs3.find_all('span', {'class': 'el'})[-2]
                                print(unit.text.strip())
                                product_data = {
                                    'product_id': product_id,
                                    'name': name,
                                    'price': price,
                                    'link': product_link,
                                    'unit': unit.text.strip(),
                                    'site': 'stroymir'
                                }
                                data1.append(product_data)
                                print(product_link)
                            print(category_link2)

                            if last_page > 1:
                                for page in range(2, last_page):
                                    category_link_page = product_link + '?page={}'.format(page)
                                    try:
                                        req_page = session.get(category_link_page, headers=headers)
                                    except ConnectionError as e:
                                        print(e)
                                        continue
                                    bs_page = BeautifulSoup(req_page.text, 'html.parser')
                                    products = bs_page.find_all('div', {'class': 'good-title'})
                                    for product in products:
                                        product_link = product.find('a').attrs['href']
                                        try:
                                            req3 = session.get(product_link, headers=headers)
                                        except ConnectionError as e:
                                            print(e)
                                            continue
                                        bs3 = BeautifulSoup(req3.text, 'html.parser')
                                        price_td = bs3.find_all('td')[-3]
                                        price = float(price_td.text.strip().replace(',', '.'))
                                        product_id = bs3.find('div', {'class': 'pcard-model'}).text.strip()
                                        name = bs3.find('div', {'class': 'pcard-name'}).text.strip()
                                        unit = bs3.find_all('span', {'class': 'el'})[-2]
                                        product_data = {
                                            'product_id': product_id,
                                            'name': name,
                                            'price': price,
                                            'link': product_link,
                                            'unit': unit.text.strip(),
                                            'site': 'stroymir'
                                        }
                                        data1.append(product_data)
                                        print(product_link)
                                    print(category_link_page)

                print(category_link2)
            print(category_link)
    return save_function(data1)

@shared_task(serializer='json')
def save_function(data):
    new_count = 0
    for product_data in data:
        try:
            Data.objects.update_or_create(
                category=product_data['unit'],
                name=product_data['name'],
                product_id=product_data['product_id'],
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
