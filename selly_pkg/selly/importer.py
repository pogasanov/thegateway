import base64
import binascii
import hashlib
import json
import urllib.parse
from decimal import Decimal
from typing import List, Dict

import requests
from markdownify import markdownify as md

from gateway import Product
from selly.utils import group_by, retry

SELLY_API_URL = "http://api.selly.pl"


# pylint: disable=too-few-public-methods
class Authenticator:
    def __init__(self, api_id, app_key):
        self.api_id = api_id
        self.app_key = app_key
        self.coin = None
        self.session = requests.Session()

    def _get(self, args: dict):
        url_args = urllib.parse.urlencode(args)
        return self.session.get(f"{SELLY_API_URL}?{url_args}").json()

    def _get_coin(self):
        response = self._get({"api": self.api_id})
        return str(response["coin"])

    def get_token(self):
        if not self.coin:
            self.coin = self._get_coin()
        feed = (self.coin + self.app_key).encode()
        hex_digest = hashlib.sha256(feed).hexdigest()
        response = self._get({"key": hex_digest})
        return response["success"]["token"]


class SellyClient:
    def __init__(self, api_id, app_key):
        self.authenticator = Authenticator(api_id, app_key)
        self.session = requests.Session()
        self.token = None

    @staticmethod
    def __fix_decoding(decoded_content):
        """Tries to clean corrupted data by removing everything after end of good data"""
        return (decoded_content.decode(errors="ignore").split("]")[0] + "]").encode()

    def _parse_response(self, content: bytes):
        try:
            decoded_content = base64.b64decode(content)
        # pylint: disable=try-except-raise
        # Because we have to handle the exception on higher level
        except binascii.Error:
            raise
        try:
            return json.loads(decoded_content.decode())
        except UnicodeDecodeError:
            # sometimes API returns some corrupted data at the end of good data so we can try and fix it
            fixed_decoded_content = self.__fix_decoding(decoded_content)
            return json.loads(fixed_decoded_content)

    @retry(retries=5, exceptions=(binascii.Error,))
    def _get(self, args: dict):
        url_args = urllib.parse.urlencode(args)
        if not self.token:
            self.token = self.authenticator.get_token()
        raw_response = self.session.get(f"{SELLY_API_URL}/apig?token={self.token}&{url_args}")
        parsed_response = self._parse_response(raw_response.content)
        return parsed_response

    def _get_table(self, table_name):
        return self._get({"table": table_name})

    def get_products(self):
        return self._get_table("produkty")

    def get_products_details(self):
        details = self._get_table("produkty_wlasciwosci")
        return group_by(details, "produkt_id", False)

    def get_products_variants(self):
        variants = self._get_table("produkty_warianty")
        return group_by(variants, "produkt_id")

    def get_products_attributes(self):
        attributes = self._get_table("produkty_atrybuty")
        return group_by(attributes, "produkty_atrybut_id", False)

    def get_products_attributes_groups(self):
        groups = self._get_table("produkty_atrybuty_grupy")
        return group_by(groups, "produkty_atrybuty_grupa_id", False)

    def get_products_variants_attributes(self):
        elements = self._get_table("produkty_warianty_atrybuty")
        return group_by(elements, "produkty_wariant_id", False)

    def get_products_images(self):
        images = self._get_table("produkty_zdjecia")
        return group_by(images, "produkt_id")


# pylint: disable=too-many-instance-attributes
class SellyImporter:
    def __init__(self, api_id, app_key, shop_url):
        self.client = SellyClient(api_id, app_key)
        self.shop_url = shop_url
        self.products = None
        self.details = None
        self.variants = None
        self.attributes = None
        self.attributes_groups = None
        self.variants_attributes = None
        self.images = None

    def _download_data(self):
        self.products = self.client.get_products()
        self.details = self.client.get_products_details()
        self.variants = self.client.get_products_variants()
        self.attributes = self.client.get_products_attributes()
        self.attributes_groups = self.client.get_products_attributes_groups()
        self.variants_attributes = self.client.get_products_variants_attributes()
        self.images = self.client.get_products_images()

    def _get_variant_data(self, variant) -> Dict:
        variant_attribute = self.variants_attributes[variant["produkty_wariant_id"]]
        attribute = self.attributes[variant_attribute["produkty_atrybut_id"]]
        attribute_group = self.attributes_groups[attribute["produkty_atrybuty_grupa_id"]]
        attribute_name = attribute_group["produkty_atrybuty_grupa"]
        attribute_name = attribute_name.replace("Kolor", "color")
        attribute_name = attribute_name.replace("Rozmiar", "size")
        attribute_value = attribute["produkty_atrybut"]
        return {attribute_name: attribute_value}

    def _get_image_url(self, details, image):
        return f"{self.shop_url}/{details['zdjecia_katalog']}{image['zdjecie_nr']}.jpg"

    def _get_single_product_variants(self, product) -> List[Product]:
        product_id = product["product_id"]
        variants = self.variants[product_id]
        details = self.details[product_id]
        images = self.images[product_id]
        product_images = [self._get_image_url(details, image) for image in images]
        if not variants:
            price = Decimal(product["price"]) / (Decimal(1) + (Decimal(details["stawka_vat"] / 100)))
            return [
                Product(
                    name=product["product_name"],
                    price=price,
                    vat_percent=details["stawka_vat"],
                    stock=Decimal(details["liczba_egzemplarzy"] if details["liczba_egzemplarzy"] else 0),
                    description=md(details["opis"]),
                    description_short=md(details["opis_skrocony"]),
                    sku=details["kod_producenta"],
                    images_urls=product_images,
                    for_sale=bool(product["visible"]),
                )
            ]
        output_variants = []
        for variant in variants:
            variant_data = self._get_variant_data(variant)
            # if variant has photo number set to 0 it means that it doesn't have an image specific for variant
            if variant["zdjecie_nr"] == 0:
                variant_images = product_images
            else:
                variants_images = group_by(images, "zdjecie_nr", False)
                variant_images = [self._get_image_url(details, variants_images[variant["zdjecie_nr"]])]
            price = Decimal(variant["wariant_cena"]) / (Decimal(1) + (Decimal(variant["stawka_vat"] / 100)))
            output_variants.append(
                Product(
                    name=product["product_name"],
                    price=price,
                    vat_percent=variant["stawka_vat"],
                    stock=Decimal(variant["ilosc"] if variant["ilosc"] else 0),
                    description=md(details["opis"]),
                    description_short=md(details["opis_skrocony"]),
                    sku=variant["kod_produktu"],
                    variant_data=variant_data,
                    images_urls=variant_images,
                    for_sale=bool(product["visible"]),
                )
            )
        return output_variants

    def build_products(self):
        self._download_data()
        yield len(self.products)
        for product in self.products:
            yield self._get_single_product_variants(product)
