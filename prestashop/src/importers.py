import logging
import os
import re
import tempfile
from decimal import Decimal
from xml.etree import ElementTree

import requests
from models import Product
from simplejson import JSONDecodeError

logger = logging.getLogger(__name__)


class Prestashop:
    def __init__(self, BASE_URL, API_KEY, imageurl_prefix, language_id=None):
        self.API_HOSTNAME = BASE_URL
        self.API_KEY = API_KEY
        self.imageurl_prefix = imageurl_prefix
        self.products = dict()
        self.variants = dict()
        self.variants_reverse = dict()
        self.product_options = dict()
        self.strings_by_reference = language_id is not None
        self.language_id = language_id

    def get_variants(self):
        """
        Converts PrestaShop product_options to Gateway variants
        """
        ids = [d['id'] for d in self.get('/product_options')['product_options']]
        for id in ids:
            data = self.get(f'/product_options/{id}')['product_option']
            product_option_values = self._ids_to_list(data['associations']['product_option_values'])
            if self.strings_by_reference:
                name = self._get_by_id(self.language_id, data['public_name'])
            else:
                name = data['public_name']
            self.variants[id] = dict(name=name, options=product_option_values)
            for value in product_option_values:
                self.variants_reverse[value] = name

    def invoke(self, endpoint, method, output_format=None):
        """
        Just a wrapper to expose requests HTTP method calls without passing all the auth etc params every time.
        """
        fn = getattr(requests, method)
        if output_format:
            params = dict(output_format=output_format)
        else:
            params = dict()
        return fn(f'{self.API_HOSTNAME}/api/{endpoint}', auth=(self.API_KEY, ''), params=params)

    def head(self, endpoint):
        return self.invoke(endpoint, "head")

    def get(self, endpoint, output_format="JSON"):
        response = self.invoke(endpoint, "get", output_format)
        try:
            return response.json()
        except JSONDecodeError:
            logger.fatal(f'{response.status_code}: {response.text}')
            raise

    def _get_by_id(self, id_, data):
        """
        Needed for PrestaShop translation support.
        """
        for d in data:
            if int(d['id']) == int(id_):
                return d['value']
        raise KeyError(id_)

    def _ids_to_list(self, idlist):
        """
        converts '[{'id': '1'}, {'id': '2'}] -> [1,2]
        """
        return [int(d['id']) for d in idlist]

    def fetch_products_ids(self):
        result = self.get('products')
        return self._ids_to_list(result['products'])

    def fetch_single_product_variant(self, product_id):
        products = list()
        result = self.get(f'products/{product_id}')
        data = result['product']
        associations = data['associations']
        try:
            image_ids = self._ids_to_list(associations['images'])
        except KeyError:
            image_ids = tuple()
        try:
            ids = self._ids_to_list(associations['combinations'])
            get_variants = True
        except KeyError:
            # No variants
            ids = product_id,
            get_variants = False
        stock_level_mapping = {int(d['id_product_attribute']): int(d['id']) for d in associations['stock_availables']}

        for id_ in ids:
            stock_level_id = stock_level_mapping.get(id_, stock_level_mapping[0])
            stock_level = self.get(f'/stock_availables/{stock_level_id}')['stock_available']['quantity']
            variant_data = dict()
            if get_variants:
                # Try to load variants from "combinations"
                combination = self.get(f'/combinations/{id_}')['combination']
                logger.info(combination)
                sku_ = combination['reference']
                sku = sku_ if sku_ else data['reference']
                price_ = combination['price']
                price = Decimal(price_ if price_ else data['price'])
                associations = combination['associations']
            else:
                # Ok, this shop has no combinations.
                sku = data['reference']
                price = Decimal(data['price'])
            try:
                # But let's see if they have product_options, which are somewhat same thing?
                product_option_values = self._ids_to_list(associations['product_option_values'])
            except KeyError:
                # Product had no options / variants.
                product_option_values = tuple()
            for option_value in product_option_values:
                try:
                    variant_ = self.product_options[option_value]
                except KeyError:
                    variant_ = self.get(f'/product_option_values/{option_value}')['product_option_value']
                    self.product_options[option_value] = variant_
                value = variant_['name']
                key = self.variants_reverse[option_value]
                variant_data[key] = value

            # Translation support
            if self.strings_by_reference:
                name = self._get_by_id(1, data['name'])
                description = strip_tags(data['description'][0]['value'])
                description_short = strip_tags(data['description_short'][1]['value'])
            else:
                name = data['name']
                description = strip_tags(data['description'])
                description_short = strip_tags(data['description_short'])

            # Images
            images = list()
            for image_id in image_ids:
                # TODO: This is currently out of band just saving the URLs and do aws s3 sync to upload the images to a bucket -
                # the image data needs to be returned as part of the "Product" as a fileobject or inline-data to exporter
                # (the previous is obviously the right way to do it, but requires a context manager)
                image_url = f'/images/products/{product_id}/{image_id}'
                r = self.head(image_url)
                sha1 = r.headers.get('Content-Sha1', f'{product_id}{image_id}')
                mimetype = r.headers['Content-Type']
                filename = f'{sha1}.{mimetype.rsplit("/")[-1]}'
                logger.debug(filename)
                images.append(f'{self.imageurl_prefix}{filename}')
                fn = f"images/{filename}"
                continue  # TODO: Remove this - hack for uploading images out of band & trial and error to speed things up.
                if os.path.exists(fn):
                    logger.info(f"Skipping existing image file {fn}")
                    continue
                # TODO: This needs to implement the context manager that can be "with product.get_image() as f: upload_to_s3":ed in the exporter.
                with open(fn, "wb+") as f:
                    r = self.invoke(image_url, 'get')
                    for chunk in r.iter_content(chunk_size=1024):
                        f.write(chunk)

            products.append(Product(
                name=name,
                price=price,
                description=description,
                description_short=description_short,
                sku=sku,
                variant_data=variant_data,
                stock=Decimal(stock_level),
                images=images,
            ))
        logger.info(products)
        return products

    def fetch_single_product(self, product_id):
        result = self.get(f'products/{product_id}')

        data = result['product']
        associations = data['associations']
        image_ids = self._ids_to_list(associations['images'])
        stock_level_mapping = {int(d['id_product_attribute']): int(d['id']) for d in associations['stock_availables']}
        stock_level = self.get(f'/stock_availables/{stock_level_mapping[product_id]}')['stock_available']['quantity']
        return Product(
            name=self._get_by_id(1, data['name']),
            price=Decimal(data['price']),
            description=strip_tags(data['description'][0]['value']),
            description_short=strip_tags(data['description_short'][1]['value']),
            sku=data['reference'],
            stock=Decimal(stock_level),
            # images=images
        )

    def build_products(self):  # TODO: Add "with variants"
        self.get_variants()
        products = self.fetch_products_ids()
        total = len(products)
        for i, p in enumerate(products):
            print(f'{i}/{total}')
            yield self.fetch_single_product_variant(p)

    def fetch_product_images(self, id, image_ids):
        # For some reason API is constantly throwing 500 error if accessing with JSON
        # But XML works fine
        # TODO: This is unnecessary - self.get('/images/products/{product_id}/{image_id}') will return the actual image.
        result = requests.get(f"{self.API_HOSTNAME}/api/images/products/{id}", auth=(self.API_KEY, ''))
        tree = ElementTree.fromstring(result.content)
        return [self.download_image(image.attrib['{http://www.w3.org/1999/xlink}href']) for image in tree[0]]

    def download_image(self, url):
        # TODO: remove as unnecessary as the context manager and exporter will do this.
        result = requests.get(url, auth=(self.API_KEY, ''))
        f = tempfile.SpooledTemporaryFile()
        f.write(result.content)
        f.seek(0)
        return f


def strip_tags(in_str):
    return re.sub('<[^<]+?>', '', in_str)
