import logging
import re
import tempfile
from decimal import Decimal
from xml.etree import ElementTree

import requests
from simplejson import JSONDecodeError

from models import Product

logger = logging.getLogger(__name__)


class Prestashop:
    def __init__(self, BASE_URL, API_KEY):
        self.API_HOSTNAME = BASE_URL
        self.API_KEY = API_KEY
        self.products = dict()
        self.variants = dict()
        self.variants_reverse = dict()
        self.product_options = dict()

    def get_variants(self):
        ids = [d['id'] for d in self.get('/product_options')['product_options']]
        for id in ids:
            data = self.get(f'/product_options/{id}')['product_option']
            product_option_values = self._ids_to_list(data['associations']['product_option_values'])
            name = self._get_by_id(1, data['public_name'])
            self.variants[id] = dict(name=name, options=product_option_values)
            for value in product_option_values:
                self.variants_reverse[value] = name

    def get(self, endpoint, output_format="JSON"):
        response = requests.get(f'{self.API_HOSTNAME}/api/{endpoint}', auth=(self.API_KEY, ''), params=dict(output_format=output_format))
        try:
            return response.json()
        except JSONDecodeError:
            logger.fatal(f'{response.status_code}: {response.text}')
            raise

    def _get_by_id(self, id_, data):
        for d in data:
            if int(d['id']) == id_:
                return d['value']
        raise KeyError(id_)

    def _ids_to_list(self, idlist):
        return [int(d['id']) for d in idlist]

    def fetch_products_ids(self):
        result = self.get('products')
        return self._ids_to_list(result['products'])

    def fetch_single_product(self, product_id):
        result = self.get(f'products/{product_id}')
        data = result['product']

        associations = data['associations']
        image_ids = self._ids_to_list(associations['images'])
        variant_ids = self._ids_to_list(associations['combinations'])
        variant_data = dict()
        product_option_values = self._ids_to_list(associations['product_option_values'])
        for option_value in product_option_values:
            try:
                variant_ = self.product_options[option_value]
            except KeyError:
                variant_ = self.get(f'/product_option_values/{option_value}')['product_option_value']
                self.product_options[option_value] = variant_
            value = self._get_by_id(1, variant_['name'])
            key = self.variants_reverse[option_value]
            variant_data[key] = value

        # TODO: Get '/api/combinations/<variant_ids> and map all product_option_values + get '/api/product_option_values/<product_option_value_id>" for values and map their values to "variant types"
        # e.g. product_option 2 is Kolor/color and product_option_value 11 is czarny/Black

        # images = self.fetch_product_images(id)

        product = Product(
            name=data['name'],
            price=Decimal(data['price']),
            description=strip_tags(data['description'][0]['value']),
            description_short=strip_tags(data['description_short'][1]['value']),
            sku=data['reference'],
            variant_data=variant_data
            # images=images
        )

        # TODO: Map stock_availables to option_value's and get stock levels for all stock_available IDs
        # 'stock_availables': [{'id': '327', 'id_product_attribute': '0'},
        #                    {'id': '326', 'id_product_attribute': '246'},
        #                     {'id': '328', 'id_product_attribute': '248'}]}}

        result = requests.get(f'{self.API_HOSTNAME}/api/stock_availables/{product_id}', auth=(self.API_KEY, ''),
                              params={'output_format': 'JSON'})
        # product.stock = Decimal(result.json()['stock_available']['quantity'])
        return product

    def build_products(self):
        products = self.fetch_products_ids()
        # TODO: Fetch /product_options/ and all their IDs and set them as "variant types"
        return [self.fetch_single_product(p) for p in products]

    def fetch_product_images(self, id, image_ids):
        # For some reason API is constantly throwing 500 error if accessing with JSON
        # But XML works fine
        # TODO: This is unnecessary - self.get('/images/products/{product_id}/{image_id}') will return the actual image.
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
