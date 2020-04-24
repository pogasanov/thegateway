import json
import pathlib
import re
from decimal import Decimal
from unittest import TestCase

import responses
from gateway import Product
from magento.importers import Magento

CURRENT_DIRECTORY = pathlib.Path(__file__).parent.absolute()


def product_response(request):
    if request_is_for_configurable_products(request):
        with open(f"{CURRENT_DIRECTORY}/magento_responses/configurable_products.json") as json_file:
            resp_body = json_file.read()

    elif request_is_for_single_products(request):
        with open(f"{CURRENT_DIRECTORY}/magento_responses/simple_products.json") as json_file:
            resp_body = json_file.read()

    elif request_is_for_specific_products_by_id(request):
        page_size = int(request.params["/rest/V1/products?searchCriteria[pageSize]"])
        page_number = int(request.params["searchCriteria[currentPage]"])
        variants_required = len(request.params["searchCriteria[filter_groups][1][filters][0][value]"].split(","))
        how_many_variants_include = min(variants_required - page_size * (page_number - 1), page_size)

        with open(f"{CURRENT_DIRECTORY}/magento_responses/example_variant.json") as json_file:
            one_variant = json_file.read()
        items = ",".join([one_variant for _ in range(how_many_variants_include)])

        resp_body = f'{{"items": [{items}], "total_count": {variants_required}}}'

    else:
        resp_body = '{"items": [], "total_count": 0}'
    return 200, {}, resp_body


def request_is_for_configurable_products(request):
    return (
        "searchCriteria[filter_groups][0][filters][0][value]" in request.params
        and request.params["searchCriteria[filter_groups][0][filters][0][value]"] == "configurable"
    )


def request_is_for_single_products(request):
    return (
        "searchCriteria[filter_groups][0][filters][0][value]" in request.params
        and request.params["searchCriteria[filter_groups][0][filters][0][value]"] == "single"
    )


def request_is_for_specific_products_by_id(request):
    return (
        "searchCriteria[filter_groups][1][filters][0][field]" in request.params
        and request.params["searchCriteria[filter_groups][1][filters][0][field]"] == "entity_id"
    )


class MagentoTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.BASE_URL = "http://123.456.789.0"
        cls.API_KEY = "NOTREALAPIKEY"

    def setUp(self):
        responses.start()
        with open(f"{CURRENT_DIRECTORY}/magento_responses/store_config.json") as json_file:
            responses.add(
                responses.GET, f"{self.BASE_URL}/rest/V1/store/storeConfigs", json=json.load(json_file), status=200,
            )
        with open(f"{CURRENT_DIRECTORY}/magento_responses/attributes.json") as json_file:
            responses.add(
                responses.GET, f"{self.BASE_URL}/rest/V1/products/attributes", json=json.load(json_file), status=200,
            )
        with open(f"{CURRENT_DIRECTORY}/magento_responses/tax_rates.json") as json_file:
            responses.add(
                responses.GET, f"{self.BASE_URL}/rest/V1/taxRates/search", json=json.load(json_file), status=200,
            )
        with open(f"{CURRENT_DIRECTORY}/magento_responses/tax_rules.json") as json_file:
            responses.add(
                responses.GET, f"{self.BASE_URL}/rest/V1/taxRules/search", json=json.load(json_file), status=200,
            )
        with open(f"{CURRENT_DIRECTORY}/magento_responses/stock.json") as json_file:
            responses.add(
                responses.GET,
                re.compile(f"{self.BASE_URL}/rest/V1/stockItems/.+"),
                json=json.load(json_file),
                status=200,
            )

        responses.add(
            responses.HEAD,
            re.compile(f"{self.BASE_URL}/pub/media/catalog/product/././.+"),
            body="notrealjpg",
            status=200,
        )
        responses.add(
            responses.GET,
            re.compile(f"{self.BASE_URL}/pub/media/catalog/product/././.+"),
            body="notrealjpg",
            status=200,
        )
        responses.add_callback(
            responses.GET,
            f"{self.BASE_URL}/rest/V1/products",
            callback=product_response,
            content_type="application/json",
        )
        responses.add(
            responses.PUT,
            re.compile(f"{self.BASE_URL}/rest/V1/products/(.+)/stockItems/1"),
            json='{"1"}',
            content_type="application/json",
        )
        self.importer = Magento(self.BASE_URL, self.API_KEY)

    def tearDown(self) -> None:
        responses.stop()
        responses.reset()

    def test_throw_exception_if_more_than_1_store(self):
        with open(f"{CURRENT_DIRECTORY}/magento_responses/store_config__multiple_stores.json") as json_file:
            responses.replace(
                responses.GET, f"{self.BASE_URL}/rest/V1/store/storeConfigs", json=json.load(json_file), status=200,
            )
        with self.assertRaisesRegex(
            NotImplementedError, "Magento has more than 1 store, which is not currently supported by this importer"
        ):
            Magento(self.BASE_URL, self.API_KEY)

    def test_get_base_media_url(self):
        self.assertEqual(self.importer.base_media_url, "http://123.456.789.0/pub/media/")

    def test_get_attributes(self):
        attribute_names = [a["code"] for a in self.importer.attributes.values()]
        self.assertIn("color", attribute_names)
        self.assertIn("size", attribute_names)

    def test_get_taxes(self):
        self.assertEqual(self.importer.taxes, {2: 8.25, 3: 23, 4: 23})

    def test_can_build_single_products(self):
        products = self.importer.build_products()
        single_products = list(filter(lambda x: len(x) == 1, products))
        self.assertEqual(len(single_products), 3)
        self.assertEqual(single_products[0][0].name, "Joust Duffle Bag")
        self.assertEqual(single_products[1][0].name, "Strive Shoulder Pack")
        self.assertEqual(single_products[2][0].name, "Crown Summit Backpack")
        self.assertIsInstance(single_products[2][0].stock, Decimal)
        self.assertEqual(single_products[2][0].stock, 100)
        self.assertIsInstance(single_products[2][0].price, Decimal)
        self.assertEqual(single_products[2][0].price, 38)
        self.assertEqual(single_products[2][0].vat_percent, 8.25)
        self.assertFalse(single_products[2][0].variant_data)

    def test_can_build_configurable_products(self):
        products = list(self.importer.build_products())
        configurable_products = list(filter(lambda x: len(x) > 1, products))
        self.assertEqual(len(configurable_products), 3)
        self.assertEqual(len(configurable_products[0]), 8)
        self.assertEqual(len(configurable_products[1]), 15)
        self.assertEqual(len(configurable_products[2]), 10)
        self.assertEqual(configurable_products[0][0].variant_data, {"color": "Black", "size": "XS"})

    def test_can_update_product_stock_quantity(self):
        products = [
            Product(name="abc", sku="abc", price=Decimal(5), stock=Decimal(10)),
            Product(name="aaa", sku="aaa", price=Decimal(5), stock=Decimal(20)),
        ]
        self.importer.sync_products(products)
        # First 4 calls are on Magento instance initialization
        # but we still checks total calls count so there are no *extra* calls
        self.assertEqual(len(responses.calls), 6)
        self.assertEqual(responses.calls[4].request.url, f"{self.BASE_URL}/rest/V1/products/abc/stockItems/1")
        self.assertEqual(responses.calls[4].request.body, b'{"stock_item": {"qty": 10}}')
        self.assertEqual(responses.calls[5].request.url, f"{self.BASE_URL}/rest/V1/products/aaa/stockItems/1")
        self.assertEqual(responses.calls[5].request.body, b'{"stock_item": {"qty": 20}}')
