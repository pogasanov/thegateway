import os
from dataclasses import dataclass

import requests


@dataclass
class Product:
    name: str
    price: float


class PrestashopImporter:
    def __init__(self):
        self.API_HOSTNAME = os.environ.get('PRESTASHOP_HOSTNAME', 'http://127.0.0.1:8080')
        self.API_KEY = os.environ.get('PRESTASHOP_API_KEY', 'RZY9E7L8AP5EPSMDZSXQ2SDJXZCEXBU4')

    def fetch_products(self):
        result = requests.get(f'{self.API_HOSTNAME}/api/products', auth=(self.API_KEY, ''),
                              params={'output_format': 'JSON'})
        return result.json()['products']

    def fetch_single_product(self, id):
        result = requests.get(f'{self.API_HOSTNAME}/api/products/{id}', auth=(self.API_KEY, ''),
                              params={'output_format': 'JSON'})
        result_json = result.json()['product']
        return Product(
            name=result_json['name'],
            price=float(result_json['price'])
        )
