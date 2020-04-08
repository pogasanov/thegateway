from decimal import Decimal
from unittest import TestCase

import responses
from prestashop.importers import Prestashop

from .prestashop_responses import *


class PrestashopTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.BASE_URL = "http://123.456.789.0"
        cls.API_KEY = "NOTREALAPIKEY"
        cls.IMAGE_URL_PREFIX = "test_"
        cls.importer = Prestashop(cls.BASE_URL, cls.API_KEY, cls.IMAGE_URL_PREFIX)

        cls.DUMMY_IMAGE = b"abc"

    def assertIsProduct1(self, product):
        self.assertEqual(product.name, "Hummingbird printed t-shirt")
        self.assertEqual(product.price, Decimal("23.9"))
        self.assertEqual(product.stock, 1.0)
        self.assertEqual(
            product.description,
            "Symbol of lightness and delicacy, the hummingbird evokes curiosity and joy. Studio Design' PolyFaune collection features classic products with colorful patterns, inspired by the traditional japanese origamis. To wear with a chino or jeans. The sublimation textile printing process provides an exceptional color rendering and a color, guaranteed overtime.",
        )
        self.assertEqual(
            product.description_short,
            "Regular fit, round neckline, short sleeves. Made of extra long staple pima cotton. \r\n",
        )
        self.assertEqual(product.sku, "demo_1")
        self.assertEqual(len(product.images), 2)
        for image in product.images:
            content = image.data.read()
            self.assertEqual(content, self.DUMMY_IMAGE)

    def assertIsProduct2(self, product):
        self.assertEqual(product.name, "Not Hummingbird printed t-shirt")
        self.assertEqual(product.price, Decimal("22.9"))
        self.assertEqual(product.stock, 2.0)
        self.assertEqual(
            product.description,
            "Symbol of lightness and delicacy, the hummingbird evokes curiosity and joy. Studio Design' PolyFaune collection features classic products with colorful patterns, inspired by the traditional japanese origamis. To wear with a chino or jeans. The sublimation textile printing process provides an exceptional color rendering and a color, guaranteed overtime.",
        )
        self.assertEqual(
            product.description_short,
            "Regular fit, round neckline, short sleeves. Made of extra long staple pima cotton. \r\n",
        )
        self.assertEqual(product.sku, "demo_1")
        self.assertEqual(len(product.images), 2)

    def setUp(self):
        responses.start()
        responses.add(
            responses.GET, f"{self.BASE_URL}/api/products", json={"products": PRESTASHOP_PRODUCTS}, status=200,
        )
        responses.add(
            responses.GET, f"{self.BASE_URL}/api/products/1", json=PRESTASHOP_PRODUCT_1, status=200,
        )
        responses.add(
            responses.GET, f"{self.BASE_URL}/api/products/2", json=PRESTASHOP_PRODUCT_2, status=200,
        )
        responses.add(
            responses.GET, f"{self.BASE_URL}/api/stock_availables/1", json=PRESTASHOP_STOCK_1, status=200,
        )
        responses.add(
            responses.GET, f"{self.BASE_URL}/api/stock_availables/2", json=PRESTASHOP_STOCK_2, status=200,
        )
        responses.add(
            responses.GET, f"{self.BASE_URL}/api/images/products/1", body=PRESTASHOP_IMAGES_1, status=200,
        )
        responses.add(
            responses.GET, f"{self.BASE_URL}/api/images/products/1/1", body=self.DUMMY_IMAGE, status=200,
        )
        responses.add(
            responses.GET, f"{self.BASE_URL}/api/images/products/1/2", body=self.DUMMY_IMAGE, status=200,
        )
        responses.add(
            responses.GET, f"{self.BASE_URL}/api/images/products/2/1", body=self.DUMMY_IMAGE, status=200,
        )
        responses.add(
            responses.GET, f"{self.BASE_URL}/api/images/products/2/2", body=self.DUMMY_IMAGE, status=200,
        )
        responses.add(
            responses.Response(
                method=responses.HEAD,
                url=f"{self.BASE_URL}/api/images/products/1/1",
                headers={"Content-Sha1": "4c9f74c014613fcdf339f040313730abe5af9bdd"},
                content_type="image/jpeg",
            )
        )
        responses.add(
            responses.Response(
                method=responses.HEAD,
                url=f"{self.BASE_URL}/api/images/products/1/2",
                headers={"Content-Sha1": "01aa68df9de18cba0591132e3b5be7ca12158bc1"},
                content_type="image/jpeg",
            )
        )
        responses.add(
            responses.Response(
                method=responses.HEAD,
                url=f"{self.BASE_URL}/api/images/products/2/1",
                headers={"Content-Sha1": "4c9f74c014613fcdf339f040313730abe5af9bdd"},
                content_type="image/jpeg",
            )
        )
        responses.add(
            responses.Response(
                method=responses.HEAD,
                url=f"{self.BASE_URL}/api/images/products/2/2",
                headers={"Content-Sha1": "01aa68df9de18cba0591132e3b5be7ca12158bc1"},
                content_type="image/jpeg",
            )
        )
        responses.add(
            responses.GET, f"{self.BASE_URL}/api/images/products/2", body=PRESTASHOP_IMAGES_2, status=200,
        )
        responses.add(
            responses.GET,
            f"{self.BASE_URL}/api/product_options",
            json=PRESTASHOP_PRODUCT_OPTIONS,
            status=200,
            match_querystring=False,
        )
        responses.add(
            responses.GET,
            f"{self.BASE_URL}/api/product_options/1",
            json=PRESTASHOP_PRODUCT_OPTIONS_1,
            status=200,
            match_querystring=False,
        )
        responses.add(
            responses.GET,
            f"{self.BASE_URL}/api/product_options/2",
            json=PRESTASHOP_PRODUCT_OPTIONS_2,
            status=200,
            match_querystring=False,
        )
        responses.add(
            responses.GET,
            f"{self.BASE_URL}/api/tax_rule_groups/1",
            json=PRESTASHOP_TAX_RULE_GROUP_1,
            status=200,
            match_querystring=False,
        )
        responses.add(
            responses.GET,
            f"{self.BASE_URL}/api/combinations/1",
            json=PRESTASHOP_COMBINATION_1,
            status=200,
            match_querystring=False,
        )
        responses.add(
            responses.GET,
            f"{self.BASE_URL}/api/product_option_values/1",
            json=PRESTASHOP_PRODUCT_OPTION_VALUE_1,
            match_querystring=False,
        )
        responses.add(
            responses.GET,
            f"{self.BASE_URL}/api/product_option_values/2",
            json=PRESTASHOP_PRODUCT_OPTION_VALUE_2,
            match_querystring=False,
        )

    def tearDown(self):
        responses.stop()
        responses.reset()

    def test_can_set_parameters_with_environment_variables(self):
        self.assertEqual(self.importer.API_HOSTNAME, self.BASE_URL)
        self.assertEqual(self.importer.API_KEY, self.API_KEY)

    def test_can_fetch_prestashop_products_ids(self):
        products = self.importer.fetch_products_ids()
        self.assertEqual(products, [1, 2])

    def test_can_fetch_prestashop_single_product(self):
        ID = 1
        self.importer.variants_reverse[1] = "Size"
        self.importer.variants_reverse[2] = "Size"
        self.importer.variants_reverse[3] = "Color"
        self.importer.variants_reverse[4] = "Color"
        product = self.importer.fetch_single_product(ID)
        self.assertIsProduct1(product[0])

    def test_can_build_products_list(self):
        products = list(self.importer.build_products())
        self.assertEqual(len(products), 2)
        self.assertIsProduct1(products[0][0])
        self.assertIsProduct2(products[1][0])

    def test_can_download_image(self):
        image_file = self.importer.download_image(1, 1)
        content = image_file.data.read()
        self.assertEqual(content, self.DUMMY_IMAGE)

    def test_get_percent_value_from_tax_rule_group_name(self):
        name = "PL Standard Rate (23%)"
        percent = self.importer._get_percent_value_from_tax_rule_group_name(name)
        self.assertEqual(percent, "23")

    def test_get_tax_percent(self):
        tax_percent = self.importer._get_tax_percent(1)
        self.assertEqual(tax_percent, 23)

    def test_product_variants_have_vat_percent_set(self):
        self.importer.variants_reverse[1] = "Size"
        self.importer.variants_reverse[2] = "Size"
        self.importer.variants_reverse[3] = "Color"
        self.importer.variants_reverse[4] = "Color"
        product_variants = self.importer.fetch_single_product(1)
        self.assertTrue(all(map(lambda x: x.vat_percent == 23, product_variants)))
