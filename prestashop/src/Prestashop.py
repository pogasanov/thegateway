import os
import re
import tempfile
from xml.etree import ElementTree

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

        images = self.fetch_product_images(id)

        product = Product(
            name=result_json['name'],
            price=float(result_json['price']),
            description=strip_tags(result_json['description']),
            description_short=strip_tags(result_json['description_short']),
            sku=result_json['reference'],
            images=images
        )

        result = requests.get(f'{self.API_HOSTNAME}/api/stock_availables/{id}', auth=(self.API_KEY, ''),
                              params={'output_format': 'JSON'})
        product.stock = float(result.json()['stock_available']['quantity'])
        return product

    def build_products(self):
        products = self.fetch_products_ids()
        return [self.fetch_single_product(p) for p in products]

    def fetch_product_images(self, id):
        # For some reason API is constantly throwing 500 error if accessing with JSON
        # But XML works fine
        result = requests.get(f"{self.API_HOSTNAME}/api/images/products/{id}", auth=(self.API_KEY, ''))
        tree = ElementTree.fromstring(result.content)
        return [self.download_image(image.attrib['{http://www.w3.org/1999/xlink}href']) for image in tree[0]]

    def download_image(self, url):
        result = requests.get(url, auth=(self.API_KEY, ''))
        f = tempfile.SpooledTemporaryFile()
        f.write(result.content)
        f.seek(0)
        return f


def strip_tags(in_str):
    return re.sub('<[^<]+?>', '', in_str)
