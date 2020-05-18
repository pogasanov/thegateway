import logging
import re
from decimal import Decimal
from typing import List
from urllib.parse import urlparse

import requests
from dicttoxml import dicttoxml
from gateway.models import Product
from gateway.utils import download_image
from simplejson import JSONDecodeError

LOGGER = logging.getLogger(__name__)


# pylint: disable=too-many-instance-attributes
class Prestashop:
    PRICES_TAX_EXCLUDED_PARAMETER = "price[price][use_tax]=0&price[price][use_reduction]=0"

    def __init__(self, base_url, api_key, image_url_prefix, language_id=None):
        self.api_hostname = base_url
        self.api_key = api_key
        self.image_url_prefix = image_url_prefix
        self.products = dict()
        self.variants_reverse = dict()
        self.product_options = dict()
        self.language_id = language_id
        self.categories = dict()
        self.exporter = None

    @property
    def category_mapping_filename(self):
        return f'category_mappings_{urlparse(self.api_hostname).netloc.replace(".", "_")}'

    def get_variants(self):
        """
        Converts PrestaShop product_options to Gateway variants
        """
        product_options = self.get("product_options")["product_options"]
        product_option_ids = [product_option["id"] for product_option in product_options]
        for product_option_id in product_option_ids:
            data = self.get(f"product_options/{product_option_id}")["product_option"]
            product_option_values = self._ids_to_list(data["associations"]["product_option_values"])

            name = self._get_localised(data["public_name"])

            for value in product_option_values:
                self.variants_reverse[value] = name

    def invoke(self, endpoint, method, data=None):
        """
        Just a wrapper to expose requests HTTP method calls without passing all the auth etc params every time.
        """
        function = getattr(requests, method)
        return function(**self._build_requests_parameters(endpoint, data))

    def _build_requests_parameters(self, endpoint, data=None):
        payload = {
            "url": f"{self.api_hostname}/api/{endpoint}",
            "auth": (self.api_key, ""),
            "params": {"output_format": "JSON"},
        }
        if data:
            payload.update({"data": dicttoxml(data)})
        return payload

    def get(self, endpoint):
        response = self.invoke(endpoint, "get")
        try:
            return response.json()
        except JSONDecodeError:
            LOGGER.fatal("%s: %s", response.status_code, response.text)
            raise

    def put(self, endpoint, data):
        response = self.invoke(endpoint, "put", data)
        try:
            return response.json()
        except JSONDecodeError:
            LOGGER.fatal("%s: %s", response.status_code, response.text)
            raise

    def _get_localised(self, data):
        """
        Needed for PrestaShop translation support.
        """
        if isinstance(data, str):
            return data
        for element in data:
            if int(element["id"]) == int(self.language_id):
                return element["value"]
        raise KeyError(self.language_id)

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

    def _get_tag_guids(self, categories):
        mappings = self.exporter.get_category_mappings(self.category_mapping_filename)

        tag_guids = set()
        for integration_category in categories:
            for mapped_name in mappings[integration_category['id']]['categories']:
                tag_guids.add(self.exporter.get_category_id_by_name(mapped_name, integration_category["id"]))

        return tag_guids

    @staticmethod
    def _get_variant_sku(data, combination):
        if combination:
            variant_sku = combination["reference"]
            sku = variant_sku if variant_sku else data["reference"]
        else:
            sku = data["reference"]
        variant_id = f"{combination['id']};" if combination else ""
        return f"{data['id']};{variant_id}{sku}"

    @staticmethod
    def _get_variant_price(data, combination):
        if combination:
            variant_price = Decimal(combination["price"])
            price = Decimal(variant_price if variant_price and variant_price != 0 else data["price"])
        else:
            price = Decimal(data["price"])
        return price

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

            value = self._get_localised(variant["name"])
            key = self.variants_reverse[option_value]
            variant_data[key] = value
        return variant_data

    def _get_variant_name(self, data):
        return self._get_localised(data["name"])

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
            # PRICES_TAX_EXCLUDED_PARAMETER is needed for prices be with tax excluded and with no reduction
            combination = self.get(f"combinations/{variant_id}?{self.PRICES_TAX_EXCLUDED_PARAMETER}")["combination"]
            LOGGER.info(combination)
            associations = combination["associations"]
        else:
            combination = None

        if "images" in associations:
            images = associations["images"]
            # If variants images is [{"id": '0'}] then it means that variants don't have an image
            if images == [{"id": "0"}]:
                images = data["associations"]["images"]
        else:
            images = data["associations"]["images"]

        try:
            image_ids = self._ids_to_list(images)
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
            tag_guids=self._get_tag_guids(data["associations"].get("categories"))
        )

    def fetch_single_product(self, product_id) -> List[Product]:
        products = list()
        data = self._get_product_data(product_id)
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
        self.check_categories_are_mapped()
        self.exporter.check_mapped_categories(self.category_mapping_filename)

        self.get_variants()
        products = self.fetch_products_ids()
        total = len(products)
        for index, product in enumerate(products, 1):
            print(f"\r{index}/{total}", end='')
            yield self.fetch_single_product(product)

    def download_image(self, product_id, image_id):
        image_url = self._build_requests_parameters(f"images/products/{product_id}/{image_id}")
        return download_image(**image_url)

    @staticmethod
    def _get_product_id_and_combination_id_from_sku(sku):
        return sku.split(";")[:2]

    @staticmethod
    def _get_stock_level_id(product_data, combination_id):
        stock_available_data = product_data["associations"]["stock_availables"]
        stock_level_mapping = {int(d["id_product_attribute"]): int(d["id"]) for d in stock_available_data}
        if combination_id:
            return stock_level_mapping[int(combination_id)]
        return stock_level_mapping[0]

    def _get_product_data(self, product_id):
        # PRICES_TAX_EXCLUDED_PARAMETER is needed for prices be with tax excluded and with no reduction
        return self.get(f"products/{product_id}?{self.PRICES_TAX_EXCLUDED_PARAMETER}")["product"]

    def _get_stock_level_data(self, stock_level_id):
        return self.get(f"stock_availables/{stock_level_id}")

    def get_stock_level(self, sku):
        product_id, combination_id = self._get_product_id_and_combination_id_from_sku(sku)
        product_data = self._get_product_data(product_id)
        stock_level_id = self._get_stock_level_id(product_data, combination_id)
        stock_level_data = self._get_stock_level_data(stock_level_id)
        return stock_level_data["stock_available"]["quantity"]

    def update_product_stock_level(self, sku, stock_difference: int):
        product_id, combination_id = self._get_product_id_and_combination_id_from_sku(sku)
        product_data = self._get_product_data(product_id)
        stock_level_id = self._get_stock_level_id(product_data, combination_id)
        stock_level_data = self._get_stock_level_data(stock_level_id)
        new_stock_level = int(stock_level_data["stock_available"]["quantity"]) + stock_difference
        stock_level_data["stock_available"]["quantity"] = new_stock_level
        return self.put(f"stock_availables/{stock_level_id}", data=stock_level_data)

    def list_of_categories(self):
        categories = self.get("categories")
        categories_ids = self._ids_to_list(categories["categories"])
        for category_id in categories_ids:
            self._add_to_category_by_id(category_id)

    def _add_to_category_by_id(self, id):
        """
        Fetch category by id and add it to `self.categories`
        Will fetch parent categories if required
        """
        if id in self.categories:
            return

        response = self.get(f"categories/{id}")["category"]
        parent_id = response["id_parent"]

        if parent_id != "0":
            if parent_id not in self.categories:
                self._add_to_category_by_id(parent_id)
            category_name = f"{self.categories[parent_id]} - {self._get_localised(response['name'])}"
        else:
            category_name = self._get_localised(response['name'])

        self.categories[str(response["id"])] = category_name

    def check_categories_are_mapped(self):
        self.list_of_categories()
        mappings = self.exporter.get_category_mappings(self.category_mapping_filename)
        errors = dict()
        for category_id, category_name in self.categories.items():
            if str(category_id) not in mappings.keys():
                errors[category_id] = category_name
        if errors:
            raise NotImplementedError(f'Missing mapping for categories: {errors}')


def strip_tags(in_str):
    return re.sub("<[^<]+?>", "", in_str)
