import os
from unittest import TestCase, mock

import responses

from prestashop.src.Prestashop import Prestashop
from prestashop.src.Product import Product

PRESTASHOP_PRODUCTS = [{'id': '1'}, {'id': '2'}]
PRESTASHOP_PRODUCT_1 = {
    "product": {"id": 1, "id_manufacturer": "1", "id_supplier": "0", "id_category_default": "4", "new": None,
                "cache_default_attribute": "1", "id_default_image": "1", "id_default_combination": "1",
                "id_tax_rules_group": "1", "position_in_category": "1", "manufacturer_name": "Studio Design",
                "quantity": "0", "type": "simple", "id_shop_default": "1", "reference": "demo_1",
                "supplier_reference": "", "location": "", "width": "0.000000", "height": "0.000000",
                "depth": "0.000000", "weight": "0.000000", "quantity_discount": "0", "ean13": "", "isbn": "",
                "upc": "", "cache_is_pack": "0", "cache_has_attachments": "0", "is_virtual": "0", "state": "1",
                "additional_delivery_times": "1", "delivery_in_stock": "", "delivery_out_stock": "",
                "on_sale": "0", "online_only": "0", "ecotax": "0.000000", "minimal_quantity": "1",
                "low_stock_threshold": None, "low_stock_alert": "0", "price": "23.900000",
                "wholesale_price": "0.000000", "unity": "", "unit_price_ratio": "0.000000",
                "additional_shipping_cost": "0.00", "customizable": "0", "text_fields": "0",
                "uploadable_files": "0", "active": "1", "redirect_type": "301-category",
                "id_type_redirected": "0", "available_for_order": "1", "available_date": "0000-00-00",
                "show_condition": "0", "condition": "new", "show_price": "1", "indexed": "1",
                "visibility": "both", "advanced_stock_management": "0", "date_add": "2020-03-27 08:08:02",
                "date_upd": "2020-03-27 08:08:02", "pack_stock_type": "3", "meta_description": "",
                "meta_keywords": "", "meta_title": "", "link_rewrite": "hummingbird-printed-t-shirt",
                "name": "Hummingbird printed t-shirt",
                "description": "<p><span style=\"font-size:10pt;font-style:normal;\"><span style=\"font-size:10pt;font-style:normal;\">Symbol of lightness and delicacy, the hummingbird evokes curiosity and joy.<\/span><span style=\"font-size:10pt;font-style:normal;\"> Studio Design' PolyFaune collection features classic products with colorful patterns, inspired by the traditional japanese origamis. To wear with a chino or jeans. The sublimation textile printing process provides an exceptional color rendering and a color, guaranteed overtime.<\/span><\/span><\/p>",
                "description_short": "<p><span style=\"font-size:10pt;font-style:normal;\">Regular fit, round neckline, short sleeves. Made of extra long staple pima cotton. <\/span><\/p>\r\n<p><\/p>",
                "available_now": "", "available_later": "",
                "associations": {"categories": [{"id": "2"}, {"id": "3"}, {"id": "4"}],
                                 "images": [{"id": "1"}, {"id": "2"}],
                                 "combinations": [{"id": "1"}, {"id": "2"}, {"id": "3"}, {"id": "4"},
                                                  {"id": "5"}, {"id": "6"}, {"id": "7"}, {"id": "8"}],
                                 "product_option_values": [{"id": "1"}, {"id": "11"}, {"id": "2"}, {"id": "8"},
                                                           {"id": "3"}, {"id": "4"}],
                                 "product_features": [{"id": "1", "id_feature_value": "4"},
                                                      {"id": "2", "id_feature_value": "8"}],
                                 "stock_availables": [{"id": "1", "id_product_attribute": "0"},
                                                      {"id": "20", "id_product_attribute": "1"},
                                                      {"id": "21", "id_product_attribute": "2"},
                                                      {"id": "22", "id_product_attribute": "3"},
                                                      {"id": "23", "id_product_attribute": "4"},
                                                      {"id": "24", "id_product_attribute": "5"},
                                                      {"id": "25", "id_product_attribute": "6"},
                                                      {"id": "26", "id_product_attribute": "7"},
                                                      {"id": "27", "id_product_attribute": "8"}]}}}
PRESTASHOP_PRODUCT_2 = {
    "product": {"id": 2, "id_manufacturer": "1", "id_supplier": "0", "id_category_default": "4", "new": None,
                "cache_default_attribute": "1", "id_default_image": "1", "id_default_combination": "1",
                "id_tax_rules_group": "1", "position_in_category": "1", "manufacturer_name": "Studio Design",
                "quantity": "0", "type": "simple", "id_shop_default": "1", "reference": "demo_1",
                "supplier_reference": "", "location": "", "width": "0.000000", "height": "0.000000",
                "depth": "0.000000", "weight": "0.000000", "quantity_discount": "0", "ean13": "", "isbn": "",
                "upc": "", "cache_is_pack": "0", "cache_has_attachments": "0", "is_virtual": "0", "state": "1",
                "additional_delivery_times": "1", "delivery_in_stock": "", "delivery_out_stock": "",
                "on_sale": "0", "online_only": "0", "ecotax": "0.000000", "minimal_quantity": "1",
                "low_stock_threshold": None, "low_stock_alert": "0", "price": "22.900000",
                "wholesale_price": "0.000000", "unity": "", "unit_price_ratio": "0.000000",
                "additional_shipping_cost": "0.00", "customizable": "0", "text_fields": "0",
                "uploadable_files": "0", "active": "1", "redirect_type": "301-category",
                "id_type_redirected": "0", "available_for_order": "1", "available_date": "0000-00-00",
                "show_condition": "0", "condition": "new", "show_price": "1", "indexed": "1",
                "visibility": "both", "advanced_stock_management": "0", "date_add": "2020-03-27 08:08:02",
                "date_upd": "2020-03-27 08:08:02", "pack_stock_type": "3", "meta_description": "",
                "meta_keywords": "", "meta_title": "", "link_rewrite": "hummingbird-printed-t-shirt",
                "name": "Not Hummingbird printed t-shirt",
                "description": "<p><span style=\"font-size:10pt;font-style:normal;\"><span style=\"font-size:10pt;font-style:normal;\">Symbol of lightness and delicacy, the hummingbird evokes curiosity and joy.<\/span><span style=\"font-size:10pt;font-style:normal;\"> Studio Design' PolyFaune collection features classic products with colorful patterns, inspired by the traditional japanese origamis. To wear with a chino or jeans. The sublimation textile printing process provides an exceptional color rendering and a color, guaranteed overtime.<\/span><\/span><\/p>",
                "description_short": "<p><span style=\"font-size:10pt;font-style:normal;\">Regular fit, round neckline, short sleeves. Made of extra long staple pima cotton. <\/span><\/p>\r\n<p><\/p>",
                "available_now": "", "available_later": "",
                "associations": {"categories": [{"id": "2"}, {"id": "3"}, {"id": "4"}],
                                 "images": [{"id": "1"}, {"id": "2"}],
                                 "combinations": [{"id": "1"}, {"id": "2"}, {"id": "3"}, {"id": "4"},
                                                  {"id": "5"}, {"id": "6"}, {"id": "7"}, {"id": "8"}],
                                 "product_option_values": [{"id": "1"}, {"id": "11"}, {"id": "2"}, {"id": "8"},
                                                           {"id": "3"}, {"id": "4"}],
                                 "product_features": [{"id": "1", "id_feature_value": "4"},
                                                      {"id": "2", "id_feature_value": "8"}],
                                 "stock_availables": [{"id": "1", "id_product_attribute": "0"},
                                                      {"id": "20", "id_product_attribute": "1"},
                                                      {"id": "21", "id_product_attribute": "2"},
                                                      {"id": "22", "id_product_attribute": "3"},
                                                      {"id": "23", "id_product_attribute": "4"},
                                                      {"id": "24", "id_product_attribute": "5"},
                                                      {"id": "25", "id_product_attribute": "6"},
                                                      {"id": "26", "id_product_attribute": "7"},
                                                      {"id": "27", "id_product_attribute": "8"}]}}}


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
        OUR_PRODUCT = Product(name="Hummingbird printed t-shirt", price=23.9)

        product = self.importer.fetch_single_product(ID)
        self.assertEqual(product, OUR_PRODUCT)

    def test_can_build_products_list(self):
        OUR_PRODUCTS = [
            Product(name="Hummingbird printed t-shirt", price=23.9),
            Product(name="Not Hummingbird printed t-shirt", price=22.9)
        ]
        products = self.importer.build_products()
        self.assertEqual(products, OUR_PRODUCTS)
