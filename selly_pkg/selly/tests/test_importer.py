from decimal import Decimal
from unittest import TestCase, mock

import responses
from markdownify import markdownify as md

from gateway import Product
from selly.importer import SellyImporter
from selly.tests.common import API_ID, APP_KEY, add_responses, DUMMY_SELLY_URL, DUMMY_TOKEN
from selly.tests.selly_responses import *

DUMMY_SHOP_URL = "http://example-shop.com"


@mock.patch("selly.importer.SELLY_API_URL", DUMMY_SELLY_URL)
@mock.patch("selly.importer.Authenticator.get_token", lambda x: DUMMY_TOKEN)
class ImporterTests(TestCase):
    def setUp(self) -> None:
        responses.start()
        add_responses()
        self.importer = SellyImporter(API_ID, APP_KEY, DUMMY_SHOP_URL)

    def tearDown(self) -> None:
        responses.stop()
        responses.reset()

    def test_get_variant_data(self):
        variant = VARIANTS[0]
        expected_data = {ATTRIBUTES_GROUPS[0]["produkty_atrybuty_grupa"]: ATTRIBUTES[0]["produkty_atrybut"]}
        self.importer._download_data()
        variant_data = self.importer._get_variant_data(variant)
        self.assertEqual(variant_data, expected_data)

    def test_get_image_url(self):
        catalog = "img/products/1/"
        details = {"zdjecia_katalog": catalog}
        image = {"zdjecie_nr": 2}
        expected_image_url = f"{DUMMY_SHOP_URL}/{catalog}2.jpg"
        image_url = self.importer._get_image_url(details, image)
        self.assertEqual(image_url, expected_image_url)

    def assertIsProduct0(self, product: Product):
        self.assertEqual(product.name, PRODUCTS[0]["product_name"])
        self.assertAlmostEqual(
            product.price * (Decimal(1) + product.vat_percent / Decimal(100)), Decimal(PRODUCTS[0]["price"])
        )
        self.assertEqual(product.vat_percent, DETAILS[0]["stawka_vat"])
        self.assertEqual(product.stock, Decimal(DETAILS[0]["liczba_egzemplarzy"]))
        self.assertEqual(product.description, md(DETAILS[0]["opis"]))
        self.assertEqual(product.description_short, md(DETAILS[0]["opis_skrocony"]))
        self.assertEqual(product.sku, DETAILS[0]["kod_producenta"])
        self.assertEqual(product.variant_data, {})
        expected_images_urls_len = len([x for x in IMAGES if x["produkt_id"] == PRODUCTS[0]["product_id"]])
        self.assertEqual(len(product.images_urls), expected_images_urls_len)

    def test_get_single_product_variants_from_product_with_no_variants(self):
        self.importer._download_data()
        variants = self.importer._get_single_product_variants(PRODUCTS[0])
        self.assertIsProduct0(variants[0])

    def test_get_single_product_variants(self):
        self.importer._download_data()
        expected_len_of_variants = len([x for x in VARIANTS if x["produkt_id"] == PRODUCTS[1]["product_id"]])
        variants = self.importer._get_single_product_variants(PRODUCTS[1])
        self.assertEqual(len(variants), expected_len_of_variants)
