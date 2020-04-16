import json
import pathlib
from unittest import TestCase

import responses
from gateway import Product
from shoper.importers import Shoper


CURRENT_DIRECTORY = pathlib.Path(__file__).parent.absolute()


class ShoperTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.BASE_URL = "http://sklep.shoper.pl"
        cls.USERNAME = "ADMIN"
        cls.PASSWORD = "PASSWORD"

    def setUp(self) -> None:
        self.product = Product(sku="116", stock=99, name="Tshirt", price="259", vat_percent=23)

        responses.start()
        with open(f"{CURRENT_DIRECTORY}/authorization_response.json") as authorization_file:
            self.authorization_response = json.load(authorization_file)
            responses.add(
                responses.POST, f"{self.BASE_URL}/webapi/rest/auth", json=self.authorization_response, status=200,
            )
        with open(f"{CURRENT_DIRECTORY}/tax_response.json") as tax_file:
            self.tax_response = json.load(tax_file)
            responses.add(
                responses.GET,
                f"{self.BASE_URL}/webapi/rest/taxes?output_format=JSON",
                json=self.tax_response,
                status=200,
            )
        with open(f"{CURRENT_DIRECTORY}/products_response.json") as products_file:
            self.products_response = json.load(products_file)
            responses.add(
                responses.GET, f"{self.BASE_URL}/webapi/rest/products", json=self.products_response, status=200,
            )
        with open(f"{CURRENT_DIRECTORY}/categories_response.json") as categories_file:
            self.categories_response = json.load(categories_file)
            responses.add(
                responses.GET, f"{self.BASE_URL}/webapi/rest/categories", json=self.categories_response, status=200,
            )
        responses.add(
            responses.HEAD, f"{self.BASE_URL}/userdata/public/gfx/6bd4167ff45e02e5a97e0c79968f6ee9.jpg", status=200
        )
        responses.add(
            responses.GET, f"{self.BASE_URL}/userdata/public/gfx/6bd4167ff45e02e5a97e0c79968f6ee9.jpg", status=200
        )
        self.importer = Shoper(self.BASE_URL, self.USERNAME, self.PASSWORD, stock_update=False)

    def tearDown(self) -> None:
        responses.stop()
        responses.reset()

    def test_can_set_parameters_with_environment_variables(self):
        self.assertEqual(self.importer.api_hostname, self.BASE_URL)
        self.assertEqual(self.importer.username, self.USERNAME)

    def test_authorization(self):
        self.assertEqual(self.importer.authorize(), self.authorization_response.get("access_token"))

    def test_taxes_response(self):
        self.assertEqual(self.importer.get("taxes"), self.tax_response)

    def test_categories_response(self):
        self.assertEqual(self.importer.get("categories"), self.categories_response)

    def test_products_response(self):
        self.assertEqual(self.importer.get("products"), self.products_response)

    def test_get_one_product_data(self):
        product = self.importer.get("products").get("list")[0]
        self.importer.get_product_data(product)
        self.assertEqual(product.get("name"), self.importer.get("products").get("list")[0].get("name"))

    def test_get_variants_data(self):
        product = self.importer.get("products").get("list")[0]
        options_number = len(product.get("options"))
        products = [
            self.importer.get_product_data(product, option, options_number) for option in product.get("options")
        ]

        self.importer.get_product_data(product)
        self.assertEqual(options_number, len(products))
        for i, option in enumerate(product.get("options")):
            self.assertEqual(products[i].sku, f"{product.get('stock').get('code')}_r{option}")
            self.assertEqual(products[i].stock, 1)

    def test_get_tax_dict(self):
        taxes = [{"tax_id": 1, "value": 23}, {"tax_id": 2, "value": 8}, {"tax_id": 3, "value": 5}]
        # pylint: disable=protected-access
        tax_dict = self.importer._tax_dict(taxes)
        self.assertEqual(tax_dict.get(1), 23)
        self.assertEqual(tax_dict.get(2), 8)
        self.assertEqual(tax_dict.get(3), 5)

    def test_get_categories_dict(self):
        categories = [
            {"category_id": 1, "translations": {"pl_PL": {"name": "Buty"}}},
            {"category_id": 2, "translations": {"pl_PL": {"name": "Spodnie"}}},
            {"category_id": 3, "translations": {"pl_PL": {"name": "Inne"}}},
        ]
        # pylint: disable=protected-access
        categories_dict = self.importer._categories_dict(categories)
        self.assertEqual(categories_dict.get(1), "Buty")
        self.assertEqual(categories_dict.get(2), "Spodnie")
        self.assertEqual(categories_dict.get(3), "Inne")

    def add_single_response(self, _responses):
        page_limit = 1
        with open(f"{CURRENT_DIRECTORY}/single_product_response_list.json") as single_product_list_file:
            code_filters = json.dumps({"stock.code": self.product.sku})
            single_product_response_list = json.load(single_product_list_file)
            _responses.add(
                _responses.GET,
                f"{self.BASE_URL}/webapi/rest/products?limit={page_limit}&filters={code_filters}&output_format=JSON",
                json=single_product_response_list,
                status=200,
            )

    def test_fetch_and_update_product_stock(self):
        """
        Test fetching and then updating in one test because update is
        tightly correlated to getting the product first.
        """
        with responses.RequestsMock() as rsp:
            self.add_single_response(rsp)
            fetched_product = self.importer.fetch_product(self.product)
            self.assertEqual(fetched_product.get("code"), self.product.sku)
            with open(f"{CURRENT_DIRECTORY}/single_product_response.json") as single_product_file:
                single_product_response = json.load(single_product_file)
                rsp.add(
                    rsp.PUT,
                    f"{self.BASE_URL}/webapi/rest/products/{fetched_product.get('product_id')}",
                    json=single_product_response,
                    status=200,
                )
                update_response = self.importer.update_product_stock(self.product)
            self.assertEqual(update_response.get("code"), self.product.sku)

    def test_get_stock_for_a_product(self):
        with responses.RequestsMock() as rsp:
            self.add_single_response(rsp)
            stock = self.importer.get_stock_for_single_product(self.product)
            self.assertEqual(self.product.stock, int(stock))
