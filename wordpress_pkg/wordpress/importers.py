import logging
from collections import defaultdict
from decimal import Decimal
from typing import (
    Dict,
    Iterator,
    List,
    Set,
)
from urllib.parse import urlparse

from gateway import Product
from woocommerce import API

# pylint: disable=C0103
logger = logging.getLogger(__name__)


# pylint: disable=R0903
class WoocommerceWordPress:
    GW_PRODUCT_UNKNOWN_QUANTITY = 100001
    STOCK_AVAILABLE = "instock"
    STOCK_ON_BACKORDER = "onbackorder"
    STOCK_UNKNOWN_AVAILABLE_QUANTITY = None
    PRODUCTS_PER_PAGE = 20
    DEFAULT_TAX = 23
    TAX_COUNTRY_CODE = "PL"
    DEFAULT_TAX_CLASS = ""
    CATEGORY_DELIMITER = " > "

    def __init__(self, consumer_key: str, consumer_secret: str, base_url: str):
        self.base_url = base_url
        self.wcapi = API(url=base_url, consumer_key=consumer_key, consumer_secret=consumer_secret)
        self.is_price_with_tax = True
        self.taxes = defaultdict(lambda: self.DEFAULT_TAX)
        self.api_category_map = dict()

        self.exporter = None

    @property
    def category_mapping_filename(self):
        return f'category_mappings_{urlparse(self.base_url).netloc.replace(".", "_")}'

    def _set_price_options(self):
        """
        Fetches settings from API and checks if prices include taxes
        assume by default that prices includes them
        """
        tax_options = self.wcapi.get("settings/tax").json()
        for option_entry in tax_options:
            if option_entry["id"] == "woocommerce_prices_include_tax":
                self.is_price_with_tax = option_entry["value"] == "yes"
                return

    def _get_map_with_ids_and_category_hierarchy(self) -> Dict[int, str]:
        category_tree = defaultdict(list)
        for page in range(1, 100):
            api_categories = self.wcapi.get("products/categories", params={"page": page}).json()
            if not api_categories:
                break

            for api_cat in api_categories:
                category_tree[api_cat["parent"]].append(api_cat)

        root = category_tree[0]
        return WoocommerceWordPress._category_traversal(category_tree, root, "")

    def get_categories(self) -> Dict:
        """
        Get all categories in the shop
        """
        if not self._is_connection_established():
            return dict()

        return self._get_map_with_ids_and_category_hierarchy()

    @staticmethod
    def _category_traversal(category_tree: dict, api_categories: list, cat_hierarchy: str) -> Dict[int, str]:
        categories = dict()
        for api_category in api_categories:
            current_cat_hierarchy = WoocommerceWordPress._concat_categories(cat_hierarchy, api_category["name"])
            categories[api_category["id"]] = current_cat_hierarchy
            categories.update(
                WoocommerceWordPress._category_traversal(
                    category_tree, category_tree[api_category["id"]], current_cat_hierarchy
                )
            )
        return categories

    @staticmethod
    def _concat_categories(*cats: str) -> str:
        if cats[0] == "":
            return WoocommerceWordPress.CATEGORY_DELIMITER.join(cats[1:])

        return WoocommerceWordPress.CATEGORY_DELIMITER.join(cats)

    def _setup_taxes(self):
        """
        Fetch and save tax classes used in shop
        """
        tax_classes = self.wcapi.get("taxes/classes")
        for tax_class_entry in tax_classes.json():
            tax_class = tax_class_entry["slug"]
            self.taxes[tax_class] = 0
            class_taxes = self.wcapi.get("taxes", params={"class": tax_class, "orderby": "id"}).json()
            tax_grouped_by_priority = defaultdict(list)
            for tax_entry in class_taxes:
                tax_grouped_by_priority[tax_entry["priority"]].append(tax_entry)

            for priority in sorted(tax_grouped_by_priority.keys()):
                group = tax_grouped_by_priority[priority]
                tax_rate = 0
                for tax_entry in group:
                    # if tax is set for PL, we stop searching in this priority group
                    if tax_entry["country"] == self.TAX_COUNTRY_CODE:
                        tax_rate = tax_entry["rate"]
                        break
                    # otherwise we take first in the group that is not set for any country
                    if tax_entry["country"] == "" and tax_rate == 0:
                        tax_rate = tax_entry["rate"]

                self.taxes[tax_class] += float(tax_rate)

        self.taxes[self.DEFAULT_TAX_CLASS] = self.taxes["standard"]

    def _fetch_products_from_api(self) -> Iterator[dict]:
        """
        Fetch products from API
        """
        for page in range(1, 1000):
            response = self.wcapi.get("products", params={"page": page, "per_page": self.PRODUCTS_PER_PAGE})
            api_products = response.json()
            if not api_products:
                break
            yield from api_products

    def _get_tax(self, api_product: dict) -> float:
        """
        Get tax based on "tax class"
        """
        return self.taxes[api_product["tax_class"]]

    def _set_price_and_vat(self, gw_product: Product, api_product: dict):
        """
        Set tax and price for product
        If the price includes tax, change to net
        """
        vat = self._get_tax(api_product)
        price = float(api_product["price"])

        # if the owner of the shop didn't set vat,
        # the price is probably gross
        if vat == 0 or self.is_price_with_tax:
            if vat == 0:
                vat = self.DEFAULT_TAX

            price = Decimal(price) / (Decimal(1) + (Decimal(vat / 100)))

        gw_product.vat_percent = vat
        gw_product.price = price

    def _convert_variable_api_product(self, api_product: dict) -> List[Product]:
        """
        Convert API product of type "variable" to set of GW products
        """
        gw_products = []
        product_stock = self._get_stock(api_product)
        for api_product_variation in self._fetch_product_variations(api_product["id"]):
            if not self._is_api_product_valid(api_product_variation):
                continue

            gw_product = Product("", 0, 0)
            gw_product.name = api_product["name"]
            gw_product.sku = api_product_variation["sku"]
            gw_product.tag_guids = self._get_tag_guids(api_product)

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

    def _fetch_product_variations(self, product_id: int) -> Iterator[dict]:
        for page in range(1, 1000):
            api_product_variations = self.wcapi.get(
                f"products/{product_id}/variations", params={"page": page, "per_page": self.PRODUCTS_PER_PAGE}
            ).json()
            if not api_product_variations:
                break

            yield from api_product_variations

    # pylint: disable=R0201
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

    # pylint: disable=R0201
    def _get_images_urls(self, api_product: dict) -> List[str]:
        return [image_record["src"] for image_record in api_product["images"]]

    # pylint: disable=R0201
    def _get_tag_guids(self, api_product: dict) -> Set[str]:
        """
        Get categories of api product and convert them to gateway categories
        """
        mappings = self.exporter.get_category_mappings(self.category_mapping_filename)

        tag_guids = set()
        for integration_category in api_product["categories"]:
            for mapped_name in mappings[str(integration_category['id'])]['categories']:
                tag_guids.add(self.exporter.get_category_id_by_name(mapped_name, integration_category["id"]))

        return tag_guids

    def _get_stock(self, api_product: dict) -> int:
        stock_status = api_product["stock_status"]
        stock = 0
        if stock_status == self.STOCK_AVAILABLE:
            if api_product["stock_quantity"] is self.STOCK_UNKNOWN_AVAILABLE_QUANTITY:
                stock = self.GW_PRODUCT_UNKNOWN_QUANTITY
            else:
                stock = api_product["stock_quantity"]
        elif stock_status == self.STOCK_ON_BACKORDER:
            stock = self.GW_PRODUCT_UNKNOWN_QUANTITY

        # stock_status == outofstock
        return stock

    def _convert_simple_api_product(self, api_product: dict) -> List[Product]:
        """
        Convert API product of type "simple" to GW product
        """
        gw_product = Product("", 0, 0)
        gw_product.name = api_product["name"]
        gw_product.description = api_product["description"]
        gw_product.description_short = api_product["short_description"]
        gw_product.sku = api_product["sku"]
        gw_product.images_urls = self._get_images_urls(api_product)
        gw_product.variant_data = self._get_variants(api_product)
        gw_product.stock = self._get_stock(api_product)
        gw_product.tag_guids = self._get_tag_guids(api_product)
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
        """
        Convert API products to gateway products model
        """
        if api_product["type"] == "simple":
            return self._convert_simple_api_product(api_product)

        if api_product["type"] == "variable":
            return self._convert_variable_api_product(api_product)

        return []

    def _is_api_product_valid(self, api_product) -> bool:
        return all(
            [
                api_product["purchasable"],
                api_product["status"] == "publish",
                api_product["type"] not in ("grouped", "external") if "type" in api_product else True,
            ]
        )

    def sync_categories(self, gw_product: Product) -> Product:
        api_products = self.find_products_by_sku(gw_product.sku)
        if not api_products:
            logger.warning("Categories not found for product name=%s, sku=%s", gw_product.name, gw_product.sku)
            return None

        gw_product.tag_guids = self._get_tag_guids(api_products[0])
        return gw_product

    def find_products_by_sku(self, sku: str) -> List[dict]:
        return self.wcapi.get("products", params={"sku": sku, "per_page": 100}).json()

    def get_products(self) -> Iterator[List[Product]]:
        self.check_categories_are_mapped()
        self.exporter.check_mapped_categories(self.category_mapping_filename)

        if not self._is_connection_established():
            return []

        self._setup_taxes()
        self._set_price_options()
        self.api_category_map = self._get_map_with_ids_and_category_hierarchy()

        for api_product in self._fetch_products_from_api():
            if not self._is_api_product_valid(api_product):
                continue

            yield self._convert_api_product_to_gw_products(api_product)

        return []

    def check_categories_are_mapped(self):
        mappings = self.exporter.get_category_mappings(self.category_mapping_filename)
        for category_id, category_name in self.get_categories().items():
            if str(category_id) not in mappings.keys():
                raise NotImplementedError(f'Missing mapping for category `{category_id}` ({category_name})')

