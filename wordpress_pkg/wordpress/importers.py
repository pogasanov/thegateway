import logging
from collections import defaultdict
from typing import List, Iterator

from gateway import Product
from woocommerce import API

CONSUMER_KEY = "ck_7311e697cff297153143761909b9127188874571"
CONSUMER_SECRET = "cs_26ffecf428f177897fa87afb5b758fd9cb10c8d2"
BASE_URL = "http://a41bcc60.ngrok.io"
logger = logging.getLogger(__name__)


class WoocommerceWordPress:
    GW_PRODUCT_UNKNOWN_QUANTITY = 100001
    STOCK_AVAILABLE = "instock"
    STOCK_ON_BACKORDER = "onbackorder"
    STOCK_UNKNOWN_AVAILABLE_QUANTITY = None
    DEFAULT_TAX = 23
    TAX_COUNTRY_CODE = "PL"
    DEFAULT_TAX_CLASS = ""

    def __init__(self, consumer_key: str, consumer_secret: str, base_url: str):
        self.wcapi = API(url=base_url, consumer_key=consumer_key, consumer_secret=consumer_secret)
        self.is_price_with_tax = None
        self.taxes = defaultdict(lambda: self.DEFAULT_TAX)

    def _set_price_options(self):
        tax_options = self.wcapi.get("settings/tax").json()
        for option_entry in tax_options:
            if option_entry["id"] == "woocommerce_prices_include_tax":
                self.is_price_with_tax = option_entry["value"] == "yes"
                return

        self.is_price_with_tax = True

    def _setup_taxes(self):
        tax_classes = self.wcapi.get("taxes/classes")
        for tax_class_entry in tax_classes.json():
            tax_class = tax_class_entry["slug"]
            self.taxes[tax_class] = 0
            class_taxes = self.wcapi.get("taxes", params={"class": tax_class, "orderby": "id"}).json()
            tax_grouped_by_priority = defaultdict(lambda: list())
            for tax_entry in class_taxes:
                tax_grouped_by_priority[tax_entry["priority"]].append(tax_entry)

            for priority in sorted(tax_grouped_by_priority.keys()):
                group = tax_grouped_by_priority[priority]
                tax_rate = 0
                for tax_entry in group:
                    if tax_entry["country"] == self.TAX_COUNTRY_CODE:
                        tax_rate = tax_entry["rate"]
                        break

                    if tax_entry["country"] == "" and tax_rate == 0:
                        tax_rate = tax_entry["rate"]

                self.taxes[tax_class] += float(tax_rate)

        self.taxes[self.DEFAULT_TAX_CLASS] = self.taxes["standard"]

    def _fetch_products_from_api(self, page=1) -> List[dict]:
        """
        Fetch products from API
        """
        response = self.wcapi.get("products", params={"page": page})
        return response.json()

    def _get_vat(self, api_product: dict) -> int:
        return self.taxes[api_product["tax_class"]]

    def _set_price_and_vat(self, gw_product: Product, api_product: dict):
        """
        Set tax and price for product
        If the price does not include tax, add it
        """
        vat = self._get_tax(api_product)
        price = float(api_product["price"])
        if not self.is_price_with_tax:
            price += price * (vat / 100)

        gw_product.price = price
        gw_product.vat_percent = vat

    def _convert_variable_api_product(self, api_product: dict) -> List[Product]:
        """
        Convert API product of type "variable" to set of GW products
        """
        api_product_variations = self.wcapi.get(f"products/{api_product['id']}/variations").json()
        gw_products = []
        product_stock = self._get_stock(api_product)
        for api_product_variation in api_product_variations:
            if not self._is_api_product_valid(api_product_variation):
                continue

            gw_product = Product("", 0, 0)
            gw_product.name = api_product["name"]
            gw_product.sku = api_product_variation["sku"]

            variant_description = api_product_variation["description"]
            if not variant_description:
                variant_description = api_product["description"]
            gw_product.description = variant_description

            variant_stock = self._get_stock(api_product_variation)
            if variant_stock == self.GW_PRODUCT_UNKNOWN_QUANTITY:
                variant_stock = product_stock
            gw_product.stock = variant_stock

            gw_product.description_short = api_product["short_description"]
            if api_product_variation["image"]:
                gw_product.images_urls = [api_product_variation["image"]["src"]]
            else:
                gw_product.images_urls = self._get_images_urls(api_product)

            gw_product.variant_data = self._get_variants(api_product_variation)
            self._set_price_and_vat(gw_product, api_product_variation)

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
        gw_product.sku = api_product["sku"]
        gw_product.images_urls = self._get_images_urls(api_product)
        gw_product.variant_data = self._get_variants(api_product)
        self._set_price_and_vat(gw_product, api_product)
        return [gw_product]

    def _is_connection_established(self) -> bool:
        """
        Make a request to API in order to check if credentials are valid
        """
        response = self.wcapi.get("products", params={"per_page": 1, "page": 1})

        if response.status_code == 401:
            logger.error("Invalid credentials (code 401)")
            return False

        if response.status_code == 404:
            logger.error("Invalid BASE_URL or permalinks (https://stackoverflow.com/a/46326542)")
            return False

        if response.status_code != 200:
            logger.error("Error occurred (code %s)", response.status_code)
            return False

        return True

    def _convert_api_product_to_gw_products(self, api_product: dict) -> List[Product]:
        if api_product["type"] == "simple":
            return self._convert_simple_api_product(api_product)

        if api_product["type"] == "variable":
            return self._convert_variable_api_product(api_product)

    def _is_api_product_valid(self, api_product) -> bool:
        return all(
            [
                api_product["purchasable"],
                api_product["status"] == "publish",
                api_product["type"] not in ("grouped", "external") if "type" in api_product else True,
            ]
        )

    def get_products(self) -> Iterator[List[Product]]:
        if not self._is_connection_established():
            return []

        self._setup_taxes()
        self._set_price_options()

        for page in range(1, 1000):
            api_products = self._fetch_products_from_api(page=page)
            if not api_products:
                return []
            for api_product in api_products:
                if not self._is_api_product_valid(api_product):
                    continue

                yield self._convert_api_product_to_gw_products(api_product)
