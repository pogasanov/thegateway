import json
import xml.etree.ElementTree as ET
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch

import responses
from idosell.importers import IdoSell

from .idosell_responses import (
    PRODUCTS_XML,
    FULL_URL,
    PRODUCT_XML,
    SUCCESSFUL_AUTHORIZATION_RESPONSE,
    INVALID_AUTHORIZATION_RESPONSE,
    PRODUCT_XML_WITHOUT_DESCRIPTION,
)


# pylint: disable=W0613
class IdoSellTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.BASE_URL = "http://testurl.com"
        cls.API_PART = "/marketplace-api/?gate=Products/getProductsFeed/5/json"
        cls.FULL_URL = "http://testurl.com/marketplace-api/?gate=Products/getProductsFeed/5/json"
        cls.EXPORT_SUCCESSFUL = f"{cls.BASE_URL}/export_successful"
        cls.INVALID_AUTH_URL = f"{cls.BASE_URL}/invalid"

        cls.IDOSELL_INIT_ARGS = {"login": "user", "password": "password", "base_url": cls.BASE_URL}

    def setUp(self) -> None:
        responses.start()
        responses.add(
            responses.Response(
                method=responses.GET, url=self.FULL_URL, status=200, body=json.dumps(SUCCESSFUL_AUTHORIZATION_RESPONSE)
            )
        )
        responses.add(
            responses.Response(
                method=responses.GET,
                url=self.INVALID_AUTH_URL + self.API_PART,
                status=200,
                body=json.dumps(INVALID_AUTHORIZATION_RESPONSE),
            )
        )
        responses.add(
            responses.Response(
                method=responses.GET,
                status=200,
                url="http://testurl.com/export_successful",
                headers={"Content-disposition": "attachment; filename=gateway.xml"},
                content_type="application/octetstream",
                body=FULL_URL,
            ),
        )
        responses.add(
            responses.Response(
                method=responses.GET,
                status=200,
                url="http://testurl.com/export_successful_xml_full",
                headers={"Content-disposition": "attachment; filename=gateway.xml"},
                content_type="application/octetstream",
                body=PRODUCTS_XML,
            )
        )

    def test_get_file(self):
        importer = IdoSell(**self.IDOSELL_INIT_ARGS)
        # pylint: disable=W0212
        file_data = importer._get_xml_with_products()
        self.assertEqual(file_data, PRODUCTS_XML)

    def test_get_file_do_not_return_xml(self):
        importer = IdoSell(**{**self.IDOSELL_INIT_ARGS, "base_url": self.INVALID_AUTH_URL})
        # pylint: disable=W0212
        file_data = importer._get_xml_with_products()
        self.assertEqual(file_data, None)

    # pylint: disable=R0201
    def get_product_by_variants(self, products, variants):
        str_variants = json.dumps(variants)
        for product in products:
            str_product_variants = json.dumps(product.variant_data)
            if str_variants == str_product_variants:
                return product

        return None

    def test_get_products(self):
        with patch("idosell.importers.date") as mock_datetime:
            mock_datetime.today.return_value = datetime(2020, 4, 6)
            importer = IdoSell(**self.IDOSELL_INIT_ARGS)
            gw_product_variants = list(importer.get_products())
            # flat list
            gw_products = [prod for variants in gw_product_variants for prod in variants]
            sku_products = [p.sku for p in gw_products]

            # check unifying sku, there are two products with different id but in the same group
            self.assertEqual(len(set(sku_products)), 1)

            self.assertEqual(len(gw_products), 10)

            available_product_with_stock = self.get_product_by_variants(
                gw_products, variants={"size": "M", "kolor": ["szary"], "kruszec": ["bawełna", "kaszmir"]}
            )
            self.assertEqual(available_product_with_stock.stock, 8)

            available_product_without_stock = self.get_product_by_variants(
                gw_products, variants={"size": "XL", "kolor": ["szary"], "kruszec": ["bawełna", "kaszmir"]}
            )
            self.assertGreater(available_product_without_stock.stock, 100000)

            unavailable_product = self.get_product_by_variants(
                gw_products, variants={"size": "XS", "kolor": ["szary"], "kruszec": ["bawełna", "kaszmir"]}
            )
            self.assertEqual(unavailable_product.stock, 0)

            # check scraping
            beige_xs_product = self.get_product_by_variants(
                gw_products, variants={"size": "XS", "kolor": ["beżowy"], "kruszec": ["bawełna"]}
            )
            self.assertEqual(beige_xs_product.name, "Bluzka damska H&M")
            self.assertEqual(
                beige_xs_product.description_short,
                "Bluzka damska  H&M z długim rękawem, ciekawymi rozcięciami na ramionach",
            )
            self.assertEqual(beige_xs_product.price, 1518)

    def test_get_product_from_xml(self):
        importer = IdoSell(**self.IDOSELL_INIT_ARGS)
        xml_product = ET.fromstring(PRODUCT_XML)
        # pylint: disable=W0212
        product = importer._get_product(xml_product=xml_product)

        self.assertEqual(product["name"], "Bluzka damska H&M")
        self.assertEqual(product["vat"], 23.0)
        self.assertEqual(product["brief"], "Bluzka damska  H&M z długim rękawem, ciekawymi rozcięciami na ramionach")
        self.assertEqual(len(product["image_urls"]), 2)
        self.assertEqual(len(product["variant_data"]), 3)
        self.assertEqual(len(product["variant_data"]["size"]), 5)
        self.assertEqual(product["variant_data"]["size"][0]["price"], 1518)
        self.assertEqual(product["variant_data"]["size"][0]["name"], "XS")
        self.assertIn("beżowy", product["variant_data"]["kolor"])

    def test_get_product_from_xml_without_short_description(self):
        importer = IdoSell(**self.IDOSELL_INIT_ARGS)
        xml_product = ET.fromstring(PRODUCT_XML_WITHOUT_DESCRIPTION)
        # pylint: disable=W0212
        product = importer._get_product(xml_product=xml_product)

        self.assertEqual(product["name"], "Triaction Sportowe Etui")
        self.assertEqual(product["brief"], "")
