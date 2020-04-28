from decimal import Decimal
from unittest import TestCase

import responses
from markdownify import markdownify as md

from gateway import Product
from sellingo.importer import Sellingo

from .sellingo_responses import *


class SellingoTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.api_url = "http://example.com"
        cls.api_key = "2137"
        cls.importer = Sellingo(cls.api_url, cls.api_key)

    def setUp(self) -> None:
        responses.start()
        responses.add(responses.GET, f"{self.api_url}/products/", json=PRODUCTS)
        responses.add(responses.GET, f"{self.api_url}/products/476/", json=PRODUCT_476)
        responses.add(responses.GET, f"{self.api_url}/products/477/", json=PRODUCT_477)
        responses.add(responses.GET, f"{self.api_url}/variants_groups/2/", json=VARIANT_GROUP_2)

    def tearDown(self) -> None:
        responses.stop()
        responses.reset()

    def test_get_variant_data(self):
        variant_data = self.importer._get_variant_data(PRODUCT_477, PRODUCT_477["variants"][0])
        self.assertEqual(variant_data, {"color": "blue"})

    def assertIsProduct476(self, product: Product):
        self.assertEqual(product.name, PRODUCT_476["title"])
        self.assertEqual(product.price, Decimal(PRODUCT_476["price"]))
        self.assertEqual(product.vat_percent, int(PRODUCT_476["vat"]))
        self.assertEqual(product.stock, Decimal(PRODUCT_476["quantity"]))
        self.assertEqual(product.description, md(PRODUCT_476["description"][0]["content"]))
        self.assertEqual(product.description_short, md(PRODUCT_476["description"][2]["content"]))
        self.assertEqual(product.images_urls, [x["original"] for x in PRODUCT_476["images"]])
        self.assertEqual(product.variant_data, {})

    def assertIsVariant0(self, product: Product):
        self.assertEqual(product.name, PRODUCT_477["title"])
        self.assertEqual(product.price, Decimal(PRODUCT_477["price"]))
        self.assertEqual(product.vat_percent, int(PRODUCT_477["vat"]))
        self.assertEqual(product.stock, Decimal(PRODUCT_477["variants"][0]["quantity"]))
        self.assertEqual(product.description, md(PRODUCT_477["description"][0]["content"]))
        self.assertEqual(product.description_short, md(PRODUCT_477["description"][2]["content"]))
        self.assertEqual(product.images_urls, [x["original"] for x in PRODUCT_477["images"]])
        self.assertEqual(product.variant_data, {"color": "blue"})

    def test_get_product(self):
        description = md(PRODUCT_476["description"][0]["content"])
        description_short = md(PRODUCT_476["description"][2]["content"])
        product = self.importer._get_product(PRODUCT_476, description, description_short)
        self.assertIsProduct476(product)

    def test_get_product_variant(self):
        description = md(PRODUCT_477["description"][0]["content"])
        description_short = md(PRODUCT_477["description"][2]["content"])
        variant = PRODUCT_477["variants"][0]
        product = self.importer._get_product(PRODUCT_477, description, description_short, variant)
        self.assertIsVariant0(product)

    def test_get_single_product_variants_when_no_variants(self):
        variants = self.importer._get_single_product_variants(PRODUCTS[0])
        self.assertIsProduct476(variants[0])
        self.assertEqual(len(variants), 1)

    def test_get_single_product_variants(self):
        variants = self.importer._get_single_product_variants(PRODUCTS[1])
        self.assertEqual(len(variants), 2)

    def test_get_product_id_and_variant_id_from_sku(self):
        parameters = (("477;4;", "477", "4"), ("476;", "476", ""))
        for sku, expected_product_id, expected_variant_id in parameters:
            with self.subTest():
                product_id, variant_id = self.importer._get_product_id_and_variant_id_from_sku(sku)
                self.assertEqual(product_id, expected_product_id)
                self.assertEqual(variant_id, expected_variant_id)

    def test_get_product_stock_level(self):
        parameters = (
            ("476;", Decimal("0.000")),
            ("477;4;", Decimal("21.000")),
            ("477;5;", Decimal("37.000")),
            ("477;", Decimal("58.000")),
        )
        for sku, expected_stock_level in parameters:
            with self.subTest():
                stock_level = self.importer.get_product_stock_level(sku)
                self.assertEqual(stock_level, expected_stock_level)

    def test_clean_group_name(self):
        parameters = (("Kolor", "color"), ("Rozmiar", "size"))
        for name, expected_name in parameters:
            with self.subTest():
                output = self.importer._clean_group_name(name)
                self.assertEqual(output, expected_name)

    def test_get_variant_sku(self):
        parameters = (
            (PRODUCT_477, PRODUCT_477["variants"][0], f"477;4;{PRODUCT_477['variants'][0]['catalog']}"),
            (PRODUCT_476, None, f"476;{PRODUCT_476['catalog_number']}"),
        )
        for product, variant, expected_sku in parameters:
            with self.subTest():
                sku = self.importer._get_variant_sku(product, variant)
                self.assertEqual(sku, expected_sku)
