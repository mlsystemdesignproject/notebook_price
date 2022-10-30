"""Скрипт для парсинга информации о ноутбуках, представленных в МВидео."""
import math
from typing import List, Dict, Union
import mvideo_config as cfg

import requests
import json
import pandas as pd
from tqdm import tqdm
import time

RequestParams = Dict[str, Dict[str, Union[str, List[str]]]]


def get_product_ids(
    request_parameters: RequestParams,
    session: requests.Session,
) -> Dict[int, List[str]]:
    """Функция выгрузки ID товаров.

    Формирует словарь, в котором:
        ключ - номер страницы, на котором представлены ноутбуки
        значение - список ID ноутбуков, представленых на данной странице
    :param request_parameters: параметры запроса для получения информации
    :param session: сессия запросов к АПИ МВидео
    :return словарь с номером страницы и списком ID представленных ноутбуков
    """
    response = session.get('https://www.mvideo.ru/bff/products/listing', **request_parameters).json()

    # Смотрим общее количество ноутбуков в магазине (на всех страницах)
    n_notebooks = response.get('body').get('total')
    # Рассчитаем сколько на одной странице представлено ноутбуков
    notebooks_per_page = (
        int(request_parameters['params']['limit'])
        if int(request_parameters['params']['limit'])
        else len(response.get('body').get('products'))
    )
    # Рассчитаем количество страниц, на которых представлены ноутбуки
    n_web_pages = math.ceil(n_notebooks / notebooks_per_page)

    # Инициализируем словарь, в котором будут все ID ноутбуков
    products_ids_per_page = {}

    # Пробегаем по всем страницам, собираем ID ноутбуков
    for page_num in tqdm(range(n_web_pages), desc='Сбор ID ноутбуков'):
        # Рассчитываем оффсет - пангинацию
        request_parameters['params']['offset'] = str(page_num * notebooks_per_page)

        page_response = session.get('https://www.mvideo.ru/bff/products/listing', **request_parameters).json()
        products_ids_per_page[page_num] = page_response.get('body').get('products')
    return products_ids_per_page


def get_product_names(
        ids_on_page: List[str],
        page_num: int,
        request_parameters: RequestParams,
        session: requests.Session,
) -> Dict[str, str]:
    """Функция выгрузки названий товаров.

    Выгружает транслитерации названий ноутбуков, которые используются в названии страниц с
    характеристиками каждого ноутбука.
    :param ids_on_page: список ID ноутбуков на странице
    :param page_num: номер страницы, на которой представлены ноутбуки
    :param request_parameters: параметры запроса для получения информации
    :param session: сессия запросов к АПИ МВидео
    :return словарь с парами ID - транслитерированное название
    """
    products_translit_name = {}
    request_parameters['json']['productIds'] = ids_on_page
    try:
        response = session.post('https://www.mvideo.ru/bff/product-details/list', **request_parameters).json()
        products_info = response.get('body').get('products')
        for product in products_info:
            products_translit_name[product['productId']] = product['nameTranslit']
    except json.decoder.JSONDecodeError:
        print(f"Could not parse notebook's names for page #{page_num}")
    return products_translit_name


def get_product_prices(
        ids_on_page: List[str],
        page_num: int,
        request_parameters: RequestParams,
        session: requests.Session,
) -> Dict[str, Dict[str, int]]:
    """Функция выгрузки цен товаров.

    Выгружает различные цены ноутбуков (базовую, акционную и выставленную на продажу)
    :param ids_on_page: список ID ноутбуков на странице
    :param page_num: номер страницы, на которой представлены ноутбуки
    :param request_parameters: параметры запроса для получения информации
    :param session: сессия запросов к АПИ МВидео
    :return словарь с парами ID - словарь с различными типами цен
    """
    product_prices_per_id = {}
    price_fields = ['basePrice', 'basePromoPrice', 'salePrice']
    request_parameters['params']['productIds'] = ','.join(ids_on_page)
    try:
        response = session.get('https://www.mvideo.ru/bff/products/prices', **request_parameters).json()
        products_prices = response.get('body').get('materialPrices')
        for product in products_prices:
            product_prices_per_id[product['productId']] = {
                price_type: product['price'][price_type] for price_type in price_fields
            }
    except json.decoder.JSONDecodeError:
        print(f"Could not parse notebook's prices for page #{page_num}")
    return product_prices_per_id


def get_product_characteristics(
        product_id: str,
        product_name_translit: str,
        request_parameters: RequestParams,
        session: requests.Session,
) -> Dict[str, Dict[str, str]]:
    """Функция выгрузки характеристик ноутбуков.

    :param product_id: ID ноутбука
    :param product_name_translit: транслитерированное название ноутбука
    :param request_parameters: параметры запроса для получения информации
    :param session: сессия запросов к АПИ МВидео
    :return словарь с парами ID - словарь с характеристиками ноутбука
    """
    request_parameters['params'] = {'productId': product_id}
    product_url = f'https://www.mvideo.ru/products/{product_name_translit}-{product_id}'
    request_parameters['headers']['referer'] = product_url
    for retry in range(5):
        try:
            response = session.get('https://www.mvideo.ru/bff/product-details', **request_parameters).json()
            product_properties = response.get('body').get('properties').get('all')
            product_parsed_stats = {
                'brand_name': response.get('body').get('brandName'),
                'url': product_url,
            }
            break
        except json.decoder.JSONDecodeError:
            if retry == 0:
                print(f"ID {product_id} will retry after 40s sleep")
                time.sleep(40)
            if retry == 4:
                print(f"ID {product_id} unsuccessful!")
                return {product_id: {'url': product_url}}

    for category in product_properties:
        for detail in category['properties']:
            product_parsed_stats[f'{category["name"]}_{detail["name"]}'] = detail['value']
    return {product_id: product_parsed_stats}


def prepare_raw_dataset(
        notebooks_stats_path: str,
        notebook_prices_path: str,
):
    """Функция сборки сырого датасета с признаками.

    Подгружает датасеты с ценами и характеристиками ноутбуков, мерджит их по ID
    и сохраняет в паркет с названием 'unfiltered_features.parquet'.
    :param notebooks_stats_path: путь до json с параметрами ноутбуков
    :param notebook_prices_path: путь до json с ценами ноутбуков
    """
    notebook_params_df = pd.read_json(notebooks_stats_path, orient='index', encoding='UTF-8')
    notebook_prices_df = pd.read_json(notebook_prices_path, orient='index', encoding='UTF-8')
    all_data = notebook_params_df.merge(
        notebook_prices_df,
        how='right',
        left_index=True,
        right_index=True,
    )
    all_data.to_parquet('unfiltered_features.parquet')


def main():
    """Функция парсинга информации о ноутбуках МВидео."""
    parser_session = requests.Session()
    # Выгружаем список всех ноутбуков
    product_ids_per_page = get_product_ids(cfg.product_ids_params, parser_session)

    all_notebooks_prices = {}
    all_notebook_names = {}
    all_notebook_stats = {}

    # Проходим каждую страницу с ноутбуками
    tqdm_info = tqdm(product_ids_per_page.items(), desc='Сбор названий и цен ноутбуков')
    for page_num, ids_on_page in tqdm_info:
        all_notebook_names.update(
            get_product_names(ids_on_page, page_num, cfg.product_names_params, parser_session)
        )
        all_notebooks_prices.update(
            get_product_prices(ids_on_page, page_num, cfg.product_prices_params, parser_session)
        )
        # Для каждого ноутбука загружаем его характеристики
        for product_id in ids_on_page:
            all_notebook_stats.update(
                get_product_characteristics(
                    product_id=product_id,
                    product_name_translit=all_notebook_names[product_id],
                    request_parameters=cfg.product_characteristics_params,
                    session=parser_session,
                )
            )
            time.sleep(0.1)

    # Сохраняем всю собранную информацию
    json_names = {
        'all_products_ids_per_page': product_ids_per_page,
        'product_prices_per_id': all_notebooks_prices,
        'product_translit_names': all_notebook_names,
        'product_characteristics': all_notebook_stats,
    }
    for file_name, data in json_names.items():
        with open(f'{file_name}.json', 'w', encoding='UTF-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    prepare_raw_dataset('product_characteristics.json', 'product_prices_per_id.json')


if __name__ == '__main__':
    main()
