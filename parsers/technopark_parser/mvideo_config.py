"""Конфигурации запросов к АПИ Мвидео."""

# Вставлять свои куки и заголовки в следующие два словаря (см. README).
cookies = {}
headers = {}

product_ids_params = {
    'cookies': cookies.copy(),
    'headers': headers.copy(),
    'params': {
        'categoryId': '118',
        'offset': '0',
        'limit': '24',
    },
}

product_names_params = {
    'cookies': cookies.copy(),
    'headers': headers.copy(),
    'json': {
        'mediaTypes': [
            'images',
        ],
        'category': True,
        'status': True,
        'brand': True,
        'propertyTypes': [
            'KEY',
        ],
        'propertiesConfig': {
            'propertiesPortionSize': 5,
        },
        'multioffer': False,
    },
}

product_prices_params = {
    'cookies': cookies.copy(),
    'headers': headers.copy(),
    'params': {
        'addBonusRubles': 'true',
        'isPromoApplied': 'true',
    },
}

product_characteristics_params = {
    'cookies': cookies.copy(),
    'headers': headers.copy(),
}
