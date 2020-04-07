import logging
import re
from decimal import Decimal
from typing import List

import requests
from simplejson import JSONDecodeError

from gateway.models import Product
from gateway.utils import download_image

logger = logging.getLogger(__name__)


class Prestashop:
    def __init__(self, BASE_URL, API_KEY, imageurl_prefix, language_id=None):
        self.API_HOSTNAME = BASE_URL
        self.API_KEY = API_KEY
        self.imageurl_prefix = imageurl_prefix
        self.products = dict()
        self.variants_reverse = dict()
        self.product_options = dict()
        self.language_id = language_id

    def get_variants(self):
        """
        Converts PrestaShop product_options to Gateway variants
        """
        ids = [d["id"] for d in self.get("product_options")["product_options"]]
        for id in ids:
            data = self.get(f"product_options/{id}")["product_option"]
            product_option_values = self._ids_to_list(
                data["associations"]["product_option_values"]
            )

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
        fn = getattr(requests, method)
        return fn(**self._build_requests_paramters(endpoint))

    def _build_requests_paramters(self, endpoint):
        return {
            "url": f"{self.API_HOSTNAME}/api/{endpoint}",
            "auth": (self.API_KEY, ""),
            "params": {"output_format": "JSON"},
        }

    def get(self, endpoint):
        response = self.invoke(endpoint, "get")
        try:
            return response.json()
        except JSONDecodeError:
            logger.fatal(f"{response.status_code}: {response.text}")
            raise

    def _get_by_id(self, id_, data):
        """
        Needed for PrestaShop translation support.
        """
        for d in data:
            if int(d["id"]) == int(id_):
                return d["value"]
        raise KeyError(id_)

    def _ids_to_list(self, idlist):
        """
        converts '[{'id': '1'}, {'id': '2'}] -> [1,2]
        """
        return [int(d["id"]) for d in idlist]

    def fetch_products_ids(self):
        result = self.get("products")
        return self._ids_to_list(result["products"])

    @staticmethod
    def _get_percent_value_from_tax_rule_group_name(name: str):
        return re.search(r"\((.*%)\)", name).group(1).rstrip("%")

    def _get_tax_percent(self, tax_rule_group_id) -> int:
        tax_rule_group = self.get(f"tax_rule_groups/{tax_rule_group_id}")[
            "tax_rule_group"
        ]
        tax_percent = self._get_percent_value_from_tax_rule_group_name(
            tax_rule_group["name"]
        )
        return int(tax_percent)

    def fetch_single_product(self, product_id) -> List[Product]:
        products = list()
        result = self.get(f"products/{product_id}")
        data = result["product"]
        tax_rule_group_id = data["id_tax_rules_group"]
        tax_percent = self._get_tax_percent(tax_rule_group_id)
        associations = data["associations"]
        try:
            image_ids = self._ids_to_list(associations["images"])
        except KeyError:
            image_ids = tuple()
        try:
            ids = self._ids_to_list(associations["combinations"])
            get_variants = True
        except KeyError:
            # No variants
            ids = (product_id,)
            get_variants = False
        stock_level_mapping = {
            int(d["id_product_attribute"]): int(d["id"])
            for d in associations["stock_availables"]
        }

        for id_ in ids:
            stock_level_id = stock_level_mapping.get(id_, stock_level_mapping[0])
            stock_level = self.get(f"stock_availables/{stock_level_id}")[
                "stock_available"
            ]["quantity"]
            variant_data = dict()
            if get_variants:
                # Try to load variants from "combinations"
                combination = self.get(f"combinations/{id_}")["combination"]
                logger.info(combination)
                sku_ = combination["reference"]
                sku = sku_ if sku_ else data["reference"]
                price_ = Decimal(combination["price"])
                price = Decimal(price_ if price_ and price_ != 0 else data["price"])
                associations = combination["associations"]
            else:
                # Ok, this shop has no combinations.
                sku = data["reference"]
                price = Decimal(data["price"])
            try:
                # But let's see if they have product_options, which are somewhat same thing?
                product_option_values = self._ids_to_list(
                    associations["product_option_values"]
                )
            except KeyError:
                # Product had no options / variants.
                product_option_values = tuple()
            for option_value in product_option_values:
                try:
                    variant_ = self.product_options[option_value]
                except KeyError:
                    variant_ = self.get(f"product_option_values/{option_value}")[
                        "product_option_value"
                    ]
                    self.product_options[option_value] = variant_

                if self.language_id:
                    value = self._get_by_id(self.language_id, variant_["name"])
                else:
                    value = variant_["name"]
                key = self.variants_reverse[option_value]
                variant_data[key] = value

            # Translation support
            if self.language_id:
                name = self._get_by_id(self.language_id, data["name"])
                description = strip_tags(
                    next(x for x in data["description"] if x["id"] == self.language_id)[
                        "value"
                    ]
                )
                description_short = strip_tags(
                    next(
                        x
                        for x in data["description_short"]
                        if x["id"] == self.language_id
                    )["value"]
                )
            else:
                name = data["name"]
                description = strip_tags(data["description"])
                description_short = strip_tags(data["description_short"])

            # Images
            images = [
                self.download_image(product_id, image_id) for image_id in image_ids
            ]

            products.append(
                Product(
                    name=name,
                    price=price,
                    description=description,
                    description_short=description_short,
                    sku=sku,
                    variant_data=variant_data,
                    stock=Decimal(stock_level),
                    vat_percent=tax_percent,
                    images=images,
                )
            )
        logger.info(products)
        return products

    def build_products(self):
        self.get_variants()
        products = self.fetch_products_ids()
        total = len(products)
        for i, p in enumerate(products, 1):
            print(f"{i}/{total}")
            yield self.fetch_single_product(p)

    def download_image(self, product_id, image_id):
        image_url = self._build_requests_paramters(
            f"images/products/{product_id}/{image_id}"
        )
        return download_image(**image_url)


def strip_tags(in_str):
    return re.sub("<[^<]+?>", "", in_str)
