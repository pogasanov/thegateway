import re
import tempfile
from decimal import Decimal
from xml.etree import ElementTree

import requests

from models import Product


class Prestashop:
    def __init__(self, BASE_URL, API_KEY):
        self.API_HOSTNAME = BASE_URL
        self.API_KEY = API_KEY

    def get(self, endpoint, output_format="JSON"):
        return requests.get(f'{self.API_HOSTNAME}/api/{endpoint}', auth=(self.API_KEY, ''), params=dict(output_format=output_format))

    def fetch_products_ids(self):
        result = self.get('products')
        return [p['id'] for p in result.json()['products']]

    def fetch_single_product(self, id):
        result = self.get(f'products/{id}')
        data = result.json()['product']

        associations = data['associations']
        image_ids = [d['id'] for d in associations['images']]
        variant_ids = [d['id'] for d in associations['combinations']]
        # TODO: Get '/api/combinations/<variant_ids> and map all product_option_values + get '/api/product_option_values/<product_option_value_id>" for values and map their values to "variant types"
        # e.g. product_option 2 is Kolor/color and product_option_value 11 is czarny/Black

        images = self.fetch_product_images(id)

        product = Product(
            name=data['name'],
            price=Decimal(data['price']),
            description=strip_tags(data['description'][0]['value']),
            description_short=strip_tags(data['description_short'][1]['value']),
            sku=data['reference'],
            images=images
        )

        # TODO: Map stock_availables to variant_id's and get stock levels for all stock_available IDs
        # 'stock_availables': [{'id': '327', 'id_product_attribute': '0'},
        #                    {'id': '326', 'id_product_attribute': '246'},
        #                     {'id': '328', 'id_product_attribute': '248'}]}}

        result = requests.get(f'{self.API_HOSTNAME}/api/stock_availables/{id}', auth=(self.API_KEY, ''),
                              params={'output_format': 'JSON'})
        product.stock = Decimal(result.json()['stock_available']['quantity'])
        return product

    def build_products(self):
        products = self.fetch_products_ids()
        # TODO: Fetch /product_options/ and all their IDs and set them as "variant types"
        return [self.fetch_single_product(p) for p in products]

    def fetch_product_images(self, id, image_ids):
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
