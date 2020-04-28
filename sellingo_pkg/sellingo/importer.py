import logging
from decimal import Decimal
from typing import List

import requests
from markdownify import markdownify as md

from gateway.models import Product

LOGGER = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class Sellingo:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.session = requests.Session()
        self.session.headers.update({"apiKey": api_key})

    def _get(self, endpoint: str) -> dict:
        response = self.session.get(f"{self.api_url}/{endpoint}")
        return response.json()

    def _get_products_data(self) -> dict:
        return self._get("products/")

    def _get_product_details_data(self, product_id) -> dict:
        return self._get(f"products/{product_id}/")

    @staticmethod
    def _clean_group_name(group_name: str) -> str:
        group_name = group_name.lower()
        group_name = group_name.replace("kolor", "color")
        group_name = group_name.replace("rozmiar", "size")
        return group_name

    def _get_variant_data(self, product_details: dict, variant_details: dict) -> dict:
        group = self._get(f"variants_groups/{product_details['variants_group_id']}/")
        group_name = self._clean_group_name(group["name"])
        return {group_name: variant_details["properties"][0]["name"]}

    @staticmethod
    def _get_variant_sku(product_details: dict, variant: dict) -> str:
        variant_id = f"{variant['id']};" if variant else ""
        sku = variant["catalog"] if variant else product_details["catalog_number"]
        product_id = f"{product_details['id']};"
        return f"{product_id}{variant_id}{sku}"

    def _get_product(
        self, product_details: dict, description: str, description_short: str, variant: dict = None
    ) -> Product:
        images = [x["original"] for x in product_details["images"]]
        product_price = Decimal(str(product_details["price"]))
        sku = self._get_variant_sku(product_details, variant)
        product = Product(
            name=product_details["title"],
            price=product_price,
            vat_percent=int(product_details["vat"]),
            stock=Decimal(str(product_details["quantity"])),
            description=description,
            description_short=description_short,
            images_urls=images,
            sku=sku,
        )
        if variant:
            product.variant_data = self._get_variant_data(product_details, variant)
            variant_price = Decimal(str(variant["price"]))
            product.price = variant_price if variant_price != Decimal(0) else product_price
            product.stock = Decimal(str(variant["quantity"]))
        return product

    def _get_single_product_variants(self, input_product: dict) -> List[Product]:
        product_details = self._get_product_details_data(input_product["id"])
        description = ""
        description_short = ""
        datacell_name_for_long_description = "Długi opis"
        datacell_name_for_short_description = "Krótki opis"
        for description_data in product_details["description"]:
            if description_data["datacell_name"] == datacell_name_for_long_description:
                description = md(description_data["content"])
            if description_data["datacell_name"] == datacell_name_for_short_description:
                description_short = md(description_data["content"])
        if "variants" not in product_details:
            return [self._get_product(product_details, description, description_short)]
        return [
            self._get_product(product_details, description, description_short, variant)
            for variant in product_details["variants"]
        ]

    def build_products(self):
        """
        First yields number of products then List[Product]
        :return:
        """
        products = self._get_products_data()
        yield len(products)
        for product in products:
            yield self._get_single_product_variants(product)

    @staticmethod
    def _get_product_id_and_variant_id_from_sku(sku: str) -> List[str]:
        if sku.count(";") > 2:
            LOGGER.warning("SKU contains more then 2 `;`: [%s]", sku)
        return sku.split(";")[:2]

    def get_product_stock_level(self, sku: str) -> Decimal:
        product_id, variant_id = self._get_product_id_and_variant_id_from_sku(sku)
        product = self._get_product_details_data(product_id)
        if variant_id and "variants" in product:
            variant = next(x for x in product["variants"] if x["id"] == variant_id)
            return Decimal(str(variant["quantity"]))
        return Decimal(str(product["quantity"]))
