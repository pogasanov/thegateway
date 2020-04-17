from typing import List, Iterator

from gateway import Product
from woocommerce import API
import logging

logger = logging.getLogger(__name__)


class WoocommerceWordPress:
    GW_PRODUCT_UNKNOWN_QUANTITY = 100001
    STOCK_AVAILABLE = "instock"
    STOCK_ON_BACKORDER = "onbackorder"
    STOCK_UNKNOWN_AVAILABLE_QUANTITY = None

    def __init__(self, consumer_key: str, consumer_secret: str, base_url: str):
        self.wcapi = API(url=base_url, consumer_key=consumer_key, consumer_secret=consumer_secret)
        self.is_price_with_tax = None
        self.taxes = None

    def _set_price_options(self):
        tax_options = wcapi.get("settings/tax").json()
        if "woocommerce_prices_include_tax" in tax_options:
            self.is_price_with_tax = tax_options["woocommerce_prices_include_tax"]["value"] == "yes"
        else:
            self.is_price_with_tax = True

    def _setup_taxes(self):
        pass

    def _fetch_products_from_api(self) -> List[dict]:
        response = self.wcapi.get("products")
        if response.status_code == 401:
            logger.error("Invalid credentials (code 401)")
            return []

        if response.status_code == 404:
            logger.error("Invalid url or invalid permalinks (https://stackoverflow.com/a/46326542)")
            return []

        if response.status_code != 200:
            logger.error("Error occurred (code %s)", response.status_code)
            return []

        return response.json()

    def _get_vat(self, api_product: dict) -> int:
        return 23  # TODO

    def _convert_variable_api_product(self, api_product: dict) -> List[Product]:
        # TODO check response?
        api_product_variations = self.wcapi.get(f"products/{api_product['id']}/variations").json()
        gw_products = []
        product_stock = self._get_stock(api_product)
        for api_product_variation in api_product_variations:
            if not self._is_api_product_valid(api_product_variation):
                continue

            gw_product = Product("", 0, 0)
            gw_product.name = api_product["name"]
            gw_product.price = api_product_variation["price"]
            gw_product.sku = api_product_variation["sku"]
            gw_product.vat_percent = self._get_vat(api_product_variation)
            variant_description = api_product_variation["description"]
            variant_stock = self._get_stock(api_product_variation)
            if variant_stock == self.GW_PRODUCT_UNKNOWN_QUANTITY:
                variant_stock = product_stock

            gw_product.stock = variant_stock
            if not variant_description:
                variant_description = api_product["description"]

            gw_product.description = variant_description
            gw_product.description_short = api_product["short_description"]
            gw_product.images = self._get_images_urls(api_product)
            gw_product.variant_data = self._get_variants(api_product_variation)

            gw_products.append(gw_product)

        return gw_products

    def _get_variants(self, api_product: dict) -> dict:
        api_variants = api_product["attributes"]
        product_variants = dict()
        for api_variant in api_variants:
            v_name = api_variant["name"].lower()
            if "option" in api_variant:
                variants = [api_variant["option"]]
            else:  # options
                variants = api_variant["options"]

            v_val = [v.lower() for v in variants]
            product_variants[v_name] = v_val

        return product_variants

    def _get_images_urls(self, api_product: dict) -> List[str]:
        return [image_record["src"] for image_record in api_product["images"]]

    def _get_categories(self, api_product: dict) -> List[str]:
        # "categories": [{"id": 17, "name": "Tshirts", "slug": "tshirts"}],
        return [cat_record["name"] for cat_record in api_product["categories"]]

    def _get_stock(self, api_product: dict) -> int:
        stock_status = api_product["stock_status"]
        if stock_status == self.STOCK_AVAILABLE:
            if api_product["stock_quantity"] is self.STOCK_UNKNOWN_AVAILABLE_QUANTITY:
                return self.GW_PRODUCT_UNKNOWN_QUANTITY
            return api_product["stock_quantity"]
        elif stock_status == self.STOCK_ON_BACKORDER:
            return self.GW_PRODUCT_UNKNOWN_QUANTITY

        # stock_status == outofstock
        return 0

    def _convert_simple_api_product(self, api_product: dict) -> List[Product]:
        gw_product = Product("", 0, 0)
        gw_product.name = api_product["name"]
        gw_product.description = api_product["description"]
        gw_product.description_short = api_product["short_description"]
        gw_product.vat_percent = self._get_vat(api_product)
        gw_product.sku = api_product["sku"]
        gw_product.price = api_product["price"]
        gw_product.images = self._get_images_urls(api_product)
        gw_product.variant_data = self._get_variants(api_product)
        return [gw_product]

    def _convert_api_product_to_gw_products(self, api_product: dict) -> List[Product]:
        if api_product["type"] == "simple":
            return self._convert_simple_api_product(api_product)

        if api_product["type"] == "variable":
            return self._convert_variable_api_product(api_product)

    def _is_api_product_valid(self, api_product) -> bool:
        return api_product["purchasable"] and api_product["status"] == "publish"

    def get_products(self) -> Iterator[List[Product]]:
        api_products = self._fetch_products_from_api()
        if not api_products:
            return

        for api_product in api_products:
            if not self._is_api_product_valid(api_product):
                continue

            yield self._convert_api_product_to_gw_products(api_product)
