import json
import os
import pathlib
import re
from unittest import TestCase
from unittest.mock import MagicMock

import responses
from wordpress.importers import WoocommerceWordPress

CURRENT_DIRECTORY = pathlib.Path(__file__).parent.absolute()

BASE_URL = "http://testurl.com"
CONSUMER_KEY = "ck_01316519b6194d8170cacb1b520e4a91e7e8d7a9"
CONSUMER_SECRET = "cs_1f9d76783dac837098b05c0229819e02c69f14d1"
API_URLS = {
    "products": BASE_URL + "/wp-json/wc/v3/products",
    "product_variations": re.compile(BASE_URL + "/wp-json/wc/v3/products/([0-9]+)/variations"),
    "settings_tax": BASE_URL + "/wp-json/wc/v3/settings/tax",
    "tax_classes": BASE_URL + "/wp-json/wc/v3/taxes/classes",
    "taxes": BASE_URL + "/wp-json/wc/v3/taxes",
    "categories": BASE_URL + "/wp-json/wc/v3/products/categories",
}


def get_json_data_from_file(file_name: str) -> str:
    try:
        with open(os.path.join(CURRENT_DIRECTORY, "woocommerce_responses", file_name)) as json_file:
            return json_file.read()
    except FileNotFoundError:
        return ""


def check_credentials(request):
    consumer_key = None
    page = request.params.get("page", 1)
    for p_key, p_val in request.params.items():
        if "consumer_key" in p_key:
            consumer_key = p_val

    headers = {"content-type": "application/json"}

    if consumer_key == CONSUMER_KEY:
        json_data = get_json_data_from_file(f"products_page_{page}.json")
        if not json_data:
            json_data = "[]"
        return 200, headers, json_data

    return 401, headers, get_json_data_from_file("invalid_credentials.json")


def get_tax_class(request):
    tax_class = request.params.get("class", None)
    headers = {"content-type": "application/json"}
    if tax_class:
        response_json = get_json_data_from_file(f"{tax_class}_tax_class.json")
    else:
        response_json = get_json_data_from_file("tax_rates.json")

    return 200, headers, response_json


def get_product_variations(request):
    matched = API_URLS["product_variations"].match(request.url).groups()
    headers = {"content-type": "application/json"}
    if not matched:
        return 400, headers, ""

    product_id = matched[0]
    page = request.params.get("page", 999)
    json_products = get_json_data_from_file(f"product_{product_id}_variations_page_{page}.json")
    if not json_products:
        json_products = "[]"
    return 200, headers, json_products


def get_categories(request):
    page = request.params.get("page", 1)
    headers = {"content-type": "application/json"}

    response_json = get_json_data_from_file(f"product_categories_page_{page}.json")
    if not response_json:
        response_json = "[]"

    return 200, headers, response_json


class WordpressWoocommerceTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pass

    def setUp(self) -> None:
        self.importer = WoocommerceWordPress(
            base_url=BASE_URL, consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET
        )
        responses.start()
        responses.add_callback(
            method=responses.GET, url=API_URLS["products"], callback=check_credentials, content_type="application/json"
        )
        responses.add_callback(
            method=responses.GET, url=API_URLS["taxes"], callback=get_tax_class, content_type="application/json"
        )
        responses.add_callback(
            method=responses.GET,
            url=API_URLS["product_variations"],
            callback=get_product_variations,
            content_type="application/json",
        )
        responses.add_callback(
            method=responses.GET, url=API_URLS["categories"], callback=get_categories, content_type="application/json",
        )

        responses.add(
            method=responses.GET,
            url=API_URLS["settings_tax"],
            content_type="application/json",
            body=get_json_data_from_file("tax_settings.json"),
        )
        responses.add(
            method=responses.GET,
            url=API_URLS["tax_classes"],
            content_type="application/json",
            body=get_json_data_from_file("tax_classes.json"),
        )

    def tearDown(self) -> None:
        responses.stop()
        responses.reset()

    def test_invalid_credentials(self):
        importer = WoocommerceWordPress(
            base_url=BASE_URL, consumer_key="invalid consumer key", consumer_secret="invalid consumer secret"
        )
        self.assertFalse(importer._is_connection_established())

    def test_set_price_options(self):
        self.importer._set_price_options()
        self.assertTrue(self.importer.is_price_with_tax)

    def test_setup_taxes(self):
        self.importer._setup_taxes()
        self.assertEqual(3, len(self.importer.taxes))
        self.assertEqual(12 + 23, self.importer.taxes["my-rate"])
        self.assertEqual(26, self.importer.taxes["standard"])
        self.assertEqual(26, self.importer.taxes[self.importer.DEFAULT_TAX_CLASS])

    def test_get_products_with_included_taxes(self):
        """
        Test fetching products (included price is read from json response)
        """
        product_json = json.loads(get_json_data_from_file("products_page_1.json"))
        products = list(self.importer.get_products())

        products_names = []
        variable_product = []
        for product_variants in products:
            product = product_variants[0]
            if product.name == "T-Shirt Red":
                variable_product = product_variants

            products_names.append(product.name)

        # all products - 2 products (external, grouped) - 1 product (type == draft)
        self.assertEqual(len(product_json) - 2 - 1, len(products))
        self.assertEqual(4, len(variable_product))
        self.assertGreaterEqual(1, len(variable_product[0].variant_data))
        self.assertNotIn("grouped product", products_names)
        self.assertNotIn("external product", products_names)
        self.assertNotIn("draft product", products_names)

        # exclude vat
        self.assertNotEqual(12, variable_product[0].price)
        self.assertNotEqual(13, variable_product[1].price)

    def test_get_category_list(self):
        categories = self.importer.get_category_list()
        self.assertIn("Clothing", categories)
        self.assertIn(self.importer.CATEGORY_DELIMITER.join(["Clothing", "Hoodies"]), categories)
        self.assertIn(
            self.importer.CATEGORY_DELIMITER.join(["Cat 1", "Cat 1-1", "Cat 1-1-2", "Cat 1-1-2-1"]), categories
        )

    def test_get_products_with_excluded_taxes(self):
        # should include vat to prices
        do_nothing = MagicMock(return_value=None)
        self.importer._set_price_options = do_nothing
        self.importer.is_price_with_tax = False
        products = list(self.importer.get_products())
        variable_product = []
        for product_variants in products:
            product = product_variants[0]
            if product.name == "T-Shirt Red":
                variable_product = product_variants

        # price is without vat
        self.assertEqual(12, variable_product[0].price)
        self.assertEqual(13, variable_product[1].price)
