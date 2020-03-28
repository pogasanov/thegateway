import os
from unittest import TestCase, mock

import responses

from prestashop.src.Prestashop import Prestashop
from prestashop.src.Product import Product
from prestashop.tests.prestashop_responses import PRESTASHOP_PRODUCTS, PRESTASHOP_PRODUCT_1, PRESTASHOP_PRODUCT_2, \
    PRESTASHOP_STOCK_1, PRESTASHOP_STOCK_2


class PrestashopTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.HOSTNAME = 'http://123.456.789.0'
        cls.API_KEY = 'NOTREALAPIKEY'
        with mock.patch.dict(os.environ, {
            'PRESTASHOP_HOSTNAME': cls.HOSTNAME,
            'PRESTASHOP_API_KEY': cls.API_KEY
        }):
            cls.importer = Prestashop()

        cls.product_1 = Product(
            name="Hummingbird printed t-shirt",
            price=23.9,
            stock=1.0,
            description="Symbol of lightness and delicacy, the hummingbird evokes curiosity and joy. Studio Design' PolyFaune collection features classic products with colorful patterns, inspired by the traditional japanese origamis. To wear with a chino or jeans. The sublimation textile printing process provides an exceptional color rendering and a color, guaranteed overtime.",
            description_short="Regular fit, round neckline, short sleeves. Made of extra long staple pima cotton. \r\n",
            sku='demo_1'
        )
        cls.product_2 = Product(
            name="Not Hummingbird printed t-shirt",
            price=22.9,
            stock=2.0,
            description="Symbol of lightness and delicacy, the hummingbird evokes curiosity and joy. Studio Design' PolyFaune collection features classic products with colorful patterns, inspired by the traditional japanese origamis. To wear with a chino or jeans. The sublimation textile printing process provides an exceptional color rendering and a color, guaranteed overtime.",
            description_short="Regular fit, round neckline, short sleeves. Made of extra long staple pima cotton. \r\n",
            sku="demo_1"
        )

    def setUp(self):
        responses.start()
        responses.add(responses.GET,
                      f'{self.HOSTNAME}/api/products',
                      json={'products': PRESTASHOP_PRODUCTS},
                      status=200)
        responses.add(responses.GET,
                      f'{self.HOSTNAME}/api/products/1',
                      json=PRESTASHOP_PRODUCT_1,
                      status=200)
        responses.add(responses.GET,
                      f'{self.HOSTNAME}/api/products/2',
                      json=PRESTASHOP_PRODUCT_2,
                      status=200)
        responses.add(responses.GET,
                      f'{self.HOSTNAME}/api/stock_availables/1',
                      json=PRESTASHOP_STOCK_1,
                      status=200)
        responses.add(responses.GET,
                      f'{self.HOSTNAME}/api/stock_availables/2',
                      json=PRESTASHOP_STOCK_2,
                      status=200)

    def tearDown(self):
        responses.stop()
        responses.reset()

    def test_can_set_parameters_with_environment_variables(self):
        self.assertEqual(self.importer.API_HOSTNAME, self.HOSTNAME)
        self.assertEqual(self.importer.API_KEY, self.API_KEY)

    def test_can_fetch_prestashop_products_ids(self):
        products = self.importer.fetch_products_ids()
        self.assertEqual(products, ['1', '2'])

    def test_can_fetch_prestashop_single_product(self):
        ID = 1
        OUR_PRODUCT = self.product_1

        product = self.importer.fetch_single_product(ID)
        self.assertEqual(product, OUR_PRODUCT)

    def test_can_build_products_list(self):
        OUR_PRODUCTS = [
            self.product_1,
            self.product_2
        ]
        products = self.importer.build_products()
        self.assertEqual(products, OUR_PRODUCTS)
