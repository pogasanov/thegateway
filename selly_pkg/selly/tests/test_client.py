from unittest import TestCase, mock

import responses
from selly.importer import SellyClient
from selly.tests.common import chain_list_of_lists, DUMMY_SELLY_URL, APP_KEY, API_ID, DUMMY_TOKEN, add_responses
from selly.tests.selly_responses import *


@mock.patch("selly.importer.SELLY_API_URL", DUMMY_SELLY_URL)
@mock.patch("selly.importer.Authenticator.get_token", lambda x: DUMMY_TOKEN)
class ClientTests(TestCase):
    def setUp(self) -> None:
        self.client = SellyClient(API_ID, APP_KEY)
        responses.start()
        add_responses()

    def tearDown(self) -> None:
        responses.stop()
        responses.reset()

    def test_get_products(self):
        products = self.client.get_products()
        self.assertEqual(products, PRODUCTS)

    def test_get_products_details(self):
        details = self.client.get_products_details()
        self.assertEqual(list(details.values()), DETAILS)

    def test_get_products_variants(self):
        variants = self.client.get_products_variants()
        self.assertEqual(chain_list_of_lists(list(variants.values())), VARIANTS)

    def test_get_products_attributes(self):
        attributes = self.client.get_products_attributes()
        self.assertEqual(list(attributes.values()), ATTRIBUTES)

    def test_get_products_attributes_groups(self):
        groups = self.client.get_products_attributes_groups()
        self.assertEqual(list(groups.values()), ATTRIBUTES_GROUPS)

    def test_get_products_variants_attributes(self):
        variants_attributes = self.client.get_products_variants_attributes()
        self.assertEqual(list(variants_attributes.values()), VARIANTS_ATTRIBUTES)

    def test_get_products_images(self):
        images = self.client.get_products_images()
        self.assertEqual(chain_list_of_lists(list(images.values())), IMAGES)

    def test_get_categories(self):
        categories = self.client.get_categories()
        self.assertEqual(categories, CATEGORIES)
