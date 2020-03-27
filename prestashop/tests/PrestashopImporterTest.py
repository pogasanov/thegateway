from unittest import TestCase

import responses

from prestashop.PrestashopImporter import PrestashopImporter


class PrestashopImporterTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.importer = PrestashopImporter()

    @responses.activate
    def test_can_fetch_prestashop_products(self):
        PRODUCTS = [{'id': '1'}, {'id': '2'}]

        responses.add(responses.GET,
                      'http://127.0.0.1:8080/api/products?output_format=JSON',
                      json={'products': PRODUCTS},
                      status=200)

        products = self.importer.fetch_products()
        self.assertEqual(len(products), len(PRODUCTS))
        self.assertEqual(products, PRODUCTS)
