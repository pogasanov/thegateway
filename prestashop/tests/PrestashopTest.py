from unittest import TestCase

import responses

from prestashop.src.Prestashop import Prestashop
from prestashop.tests.prestashop_responses import PRESTASHOP_PRODUCTS, PRESTASHOP_PRODUCT_1, PRESTASHOP_PRODUCT_2, \
    PRESTASHOP_STOCK_1, PRESTASHOP_STOCK_2, PRESTASHOP_IMAGES_1, PRESTASHOP_IMAGES_2


class PrestashopTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.BASE_URL = 'http://123.456.789.0'
        cls.API_KEY = 'NOTREALAPIKEY'
        cls.importer = Prestashop(cls.BASE_URL, cls.API_KEY)

        cls.DUMMY_IMAGE = b'abc'

    def assertIsProduct1(self, product):
        self.assertEqual(product.name, "Hummingbird printed t-shirt")
        self.assertEqual(product.price, 23.9)
        self.assertEqual(product.stock, 1.0)
        self.assertEqual(product.description,
                         "Symbol of lightness and delicacy, the hummingbird evokes curiosity and joy. Studio Design' PolyFaune collection features classic products with colorful patterns, inspired by the traditional japanese origamis. To wear with a chino or jeans. The sublimation textile printing process provides an exceptional color rendering and a color, guaranteed overtime.")
        self.assertEqual(product.description_short,
                         "Regular fit, round neckline, short sleeves. Made of extra long staple pima cotton. \r\n")
        self.assertEqual(product.sku, "demo_1")
        self.assertEqual(len(product.images), 2)
        for image in product.images:
            with image as f:
                content = f.read()
            self.assertEqual(content, self.DUMMY_IMAGE)

    def assertIsProduct2(self, product):
        self.assertEqual(product.name, "Not Hummingbird printed t-shirt")
        self.assertEqual(product.price, 22.9)
        self.assertEqual(product.stock, 2.0)
        self.assertEqual(product.description,
                         "Symbol of lightness and delicacy, the hummingbird evokes curiosity and joy. Studio Design' PolyFaune collection features classic products with colorful patterns, inspired by the traditional japanese origamis. To wear with a chino or jeans. The sublimation textile printing process provides an exceptional color rendering and a color, guaranteed overtime.")
        self.assertEqual(product.description_short,
                         "Regular fit, round neckline, short sleeves. Made of extra long staple pima cotton. \r\n")
        self.assertEqual(product.sku, "demo_1")
        self.assertEqual(len(product.images), 0)

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
        responses.add(responses.GET,
                      f'{self.HOSTNAME}/api/images/products/1',
                      body=PRESTASHOP_IMAGES_1,
                      status=200)
        responses.add(responses.GET,
                      f'{self.HOSTNAME}/api/images/products/1/1',
                      body=self.DUMMY_IMAGE,
                      status=200)
        responses.add(responses.GET,
                      f'{self.HOSTNAME}/api/images/products/1/2',
                      body=self.DUMMY_IMAGE,
                      status=200)
        responses.add(responses.GET,
                      f'{self.HOSTNAME}/api/images/products/2',
                      body=PRESTASHOP_IMAGES_2,
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

        product = self.importer.fetch_single_product(ID)
        self.assertIsProduct1(product)

    def test_can_build_products_list(self):
        products = self.importer.build_products()
        self.assertEqual(len(products), 2)
        self.assertIsProduct1(products[0])
        self.assertIsProduct2(products[1])

    def test_can_download_image(self):
        IMAGE_URL = f'{self.HOSTNAME}/api/images/products/1/1'
        image_file = self.importer.download_image(IMAGE_URL)
        with image_file as f:
            content = f.read()
        self.assertEqual(content, self.DUMMY_IMAGE)

    def test_can_fetch_product_images(self):
        ID = 1
        images = self.importer.fetch_product_images(ID)
        self.assertEqual(len(images), 2)
        for image in images:
            with image as f:
                content = f.read()
            self.assertEqual(content, self.DUMMY_IMAGE)
