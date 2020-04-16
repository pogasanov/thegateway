import logging
from typing import List

from gateway import Product
from woocommerce import API

CONSUMER_KEY = "ck_7311e697cff297153143761909b9127188874571"
CONSUMER_SECRET = "cs_26ffecf428f177897fa87afb5b758fd9cb10c8d2"
BASE_URL = "http://1a163393.ngrok.io"
logger = logging.getLogger(__name__)


class WordPressWooCommerce:
    GW_PRODUCT_UNKNOWN_QUANTITY = 100001
    STOCK_AVAILABLE = "instock"
    STOCK_ON_BACKORDER = "onbackorder"
    STOCK_UNKNOWN_AVAILABLE_QUANTITY = None

    def __init__(self, consumer_key: str, consumer_secret: str, base_url: str):
        self.wcapi = API(url=base_url, consumer_key=consumer_key, consumer_secret=consumer_secret)

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

    def _get_product_variations(self, product: dict):
        # attributes = api_
        pass

    def _get_variants(self, api_product: dict) -> List[dict]:
        api_variants = api_product["attributes"]
        product_variants = []
        for api_variant in api_variants:
            v_name = api_variant["name"].lower()
            v_val = [v.lower() for v in api_variant["options"]]
            product_variants.append({v_name: v_val})

        return product_variants

    def _get_images_urls(self, api_product: dict) -> List[str]:
        """    "images": [
        {
            "id": 43,
            "date_created": "2020-04-15T10:54:42",
            "date_created_gmt": "2020-04-15T10:54:42",
            "date_modified": "2020-04-15T10:54:42",
            "date_modified_gmt": "2020-04-15T10:54:42",
            "src": "http://681ff8a5.ngrok.io/wp-content/uploads/2020/04/tshirt-2.jpg",
            "name": "tshirt-2.jpg",
            "alt": "",
        }
    ],"""
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

    def _convert_api_product_to_gw_products(self, api_product: dict) -> List[Product]:
        # fetch_fields = ["name", "description", "short_description", "sku", "price", "categories", "attributes", "images"]
        gw_product = Product("", 0, 0)
        if api_product["type"] == "simple":
            gw_product.name = api_product["name"]
            gw_product.description = api_product["description"]
            gw_product.description_short = api_product["short_description"]
            gw_product.sku = api_product["sku"]
            gw_product.price = api_product["price"]
            gw_product.images = self._get_images_urls(api_product)
            return [gw_product]

        if api_product["type"] == "variable":
            pass

    def _is_api_product_valid(self, api_product) -> bool:
        return api_product["purchasable"]

    def get_products(self):
        api_products = self._fetch_products_from_api()
        if not api_products:
            return

        for api_product in api_products:
            if not self._is_api_product_valid(api_product):
                continue

            yield self._convert_api_product_to_gw_products(api_product)
