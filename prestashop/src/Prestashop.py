import os
import re

import requests

from prestashop.src.Product import Product


class Prestashop:
    def __init__(self):
        self.API_HOSTNAME = os.environ.get('PRESTASHOP_HOSTNAME', 'http://127.0.0.1:8080')
        self.API_KEY = os.environ.get('PRESTASHOP_API_KEY', 'RZY9E7L8AP5EPSMDZSXQ2SDJXZCEXBU4')

    def fetch_products_ids(self):
        result = requests.get(f'{self.API_HOSTNAME}/api/products', auth=(self.API_KEY, ''),
                              params={'output_format': 'JSON'})
        return [p['id'] for p in result.json()['products']]

    def fetch_single_product(self, id):
        result = requests.get(f'{self.API_HOSTNAME}/api/products/{id}', auth=(self.API_KEY, ''),
                              params={'output_format': 'JSON'})
        result_json = result.json()['product']
        product = Product(
            name=result_json['name'],
            price=float(result_json['price']),
            description=strip_tags(result_json['description']),
            description_short=strip_tags(result_json['description_short']),
            sku=result_json['reference']
        )

        result = requests.get(f'{self.API_HOSTNAME}/api/stock_availables/{id}', auth=(self.API_KEY, ''),
                              params={'output_format': 'JSON'})
        product.stock = float(result.json()['stock_available']['quantity'])
        return product

    def build_products(self):
        products = self.fetch_products_ids()
        return [self.fetch_single_product(p) for p in products]


def strip_tags(in_str):
    return re.sub('<[^<]+?>', '', in_str)
