import logging
import re
from decimal import Decimal
from typing import List

import requests
from simplejson import JSONDecodeError

from gateway.models import Product
from gateway.utils import download_image

LOGGER = logging.getLogger(__name__)


class Prestashop:
    def __init__(self, base_url, api_key, image_url_prefix, language_id=None):
        self.api_hostname = base_url
        self.api_key = api_key
        self.image_url_prefix = image_url_prefix
        self.products = dict()
        self.variants_reverse = dict()
        self.product_options = dict()
        self.language_id = language_id

    def get_variants(self):
        """
        Converts PrestaShop product_options to Gateway variants
        """
        product_options = self.get("product_options")["product_options"]
        product_option_ids = [product_option["id"] for product_option in product_options]
        for product_option_id in product_option_ids:
            data = self.get(f"product_options/{product_option_id}")["product_option"]
            product_option_values = self._ids_to_list(data["associations"]["product_option_values"])

            if self.language_id:
                name = self._get_by_id(self.language_id, data["public_name"])
            else:
                name = data["public_name"]

            for value in product_option_values:
                self.variants_reverse[value] = name

    def invoke(self, endpoint, method):
        """
        Just a wrapper to expose requests HTTP method calls without passing all the auth etc params every time.
        """
        function = getattr(requests, method)
        return function(**self._build_requests_parameters(endpoint))

    def _build_requests_parameters(self, endpoint):
        return {
            "url": f"{self.api_hostname}/api/{endpoint}",
            "auth": (self.api_key, ""),
            "params": {"output_format": "JSON"},
        }

    def get(self, endpoint):
        response = self.invoke(endpoint, "get")
        try:
            return response.json()
        except JSONDecodeError:
            LOGGER.fatal("%s: %s", response.status_code, response.text)
            raise

    @staticmethod
    def _get_by_id(_id, data):
        """
        Needed for PrestaShop translation support.
        """
        for element in data:
            if int(element["id"]) == int(_id):
                return element["value"]
        raise KeyError(_id)

    @staticmethod
    def _ids_to_list(ids):
        """
        converts '[{'id': '1'}, {'id': '2'}] -> [1,2]
        """
        return [int(d["id"]) for d in ids]

    def fetch_products_ids(self):
        result = self.get("products")
        return self._ids_to_list(result["products"])

    @staticmethod
    def _get_percent_value_from_tax_rule_group_name(name: str):
        return re.search(r"\((.*%)\)", name).group(1).rstrip("%")

    def _get_tax_percent(self, tax_rule_group_id) -> int:
        tax_rule_group = self.get(f"tax_rule_groups/{tax_rule_group_id}")["tax_rule_group"]
        tax_percent = self._get_percent_value_from_tax_rule_group_name(tax_rule_group["name"])
        return int(tax_percent)

    @staticmethod
    def _get_variant_sku(data, combination):
        if combination:
            variant_sku = combination["reference"]
            return variant_sku if variant_sku else data["reference"]
        return data["reference"]

    @staticmethod
    def _get_variant_price(data, combination):
        if combination:
            variant_price = Decimal(combination["price"])
            return Decimal(variant_price if variant_price and variant_price != 0 else data["price"])
        return data["price"]

    def _get_variant_data(self, associations):
        variant_data = dict()
        try:
            # But let's see if they have product_options, which are somewhat same thing?
            product_option_values = self._ids_to_list(associations["product_option_values"])
        except KeyError:
            # Product had no options / variants.
            product_option_values = tuple()
        for option_value in product_option_values:
            try:
                variant = self.product_options[option_value]
            except KeyError:
                variant = self.get(f"product_option_values/{option_value}")["product_option_value"]
                self.product_options[option_value] = variant

            if self.language_id:
                value = self._get_by_id(self.language_id, variant["name"])
            else:
                value = variant["name"]
            key = self.variants_reverse[option_value]
            variant_data[key] = value
        return variant_data

    def _get_variant_name(self, data):
        if self.language_id:
            return self._get_by_id(self.language_id, data["name"])
        return data["name"]

    def _get_variant_description(self, data):
        if self.language_id:
            return strip_tags(next(x for x in data["description"] if x["id"] == self.language_id)["value"])
        return strip_tags(data["description"])

    def _get_variant_short_description(self, data):
        if self.language_id:
            return strip_tags(next(x for x in data["description_short"] if x["id"] == self.language_id)["value"])
        return strip_tags(data["description_short"])

    def _get_variant(self, data, product_id, stock_level, variant_id):
        associations = data["associations"]

        if data["associations"].get("combinations"):
            combination = self.get(f"combinations/{variant_id}")["combination"]
            LOGGER.info(combination)
            associations = combination["associations"]
        else:
            combination = None

        try:
            image_ids = self._ids_to_list(associations["images"])
        except KeyError:
            image_ids = tuple()
        images = [self.download_image(product_id, image_id) for image_id in image_ids]
        return Product(
            name=self._get_variant_name(data),
            price=self._get_variant_price(data, combination),
            description=self._get_variant_description(data),
            description_short=self._get_variant_short_description(data),
            sku=self._get_variant_sku(data, combination),
            variant_data=self._get_variant_data(associations),
            stock=Decimal(stock_level),
            vat_percent=self._get_tax_percent(data["id_tax_rules_group"]),
            images=images,
        )

    def fetch_single_product(self, product_id) -> List[Product]:
        products = list()
        data = self.get(f"products/{product_id}")["product"]
        associations = data["associations"]
        try:
            variants_ids = self._ids_to_list(associations["combinations"])
        except KeyError:
            # No variants
            variants_ids = (product_id,)
        stock_level_mapping = {int(d["id_product_attribute"]): int(d["id"]) for d in associations["stock_availables"]}

        for variant_id in variants_ids:
            stock_level_id = stock_level_mapping.get(variant_id, stock_level_mapping[0])
            stock_level = self.get(f"stock_availables/{stock_level_id}")["stock_available"]["quantity"]
            variant = self._get_variant(data, product_id, stock_level, variant_id)
            products.append(variant)
        LOGGER.info(products)
        return products

    def build_products(self):
        self.get_variants()
        products = self.fetch_products_ids()
        total = len(products)
        for index, product in enumerate(products, 1):
            print(f"{index}/{total}")
            yield self.fetch_single_product(product)

    def download_image(self, product_id, image_id):
        image_url = self._build_requests_parameters(f"images/products/{product_id}/{image_id}")
        return download_image(**image_url)


def strip_tags(in_str):
    return re.sub("<[^<]+?>", "", in_str)
