import os
from unittest import TestCase, mock

import responses

from prestashop.src.Gateway import Gateway
from prestashop.src.Product import Product
from prestashop.tests.gateway_responses import GATEWAY_PRODUCT


class GatewayTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.BASE_URL = 'http://123.456.789.0'
        cls.SHOP_ID = 'a547de18-7a1d-450b-a57b-bbf7f177db84'
        cls.SECRET = 'OyB2YbwTVtRXuJv+VE4oJLVyGo8pf1XVibCk08lt4ys='
        with mock.patch.dict(os.environ, {
            'GATEWAY_BASE_URL': cls.BASE_URL,
            'GATEWAY_SHOP_ID': cls.SHOP_ID,
            'GATEWAY_SECRET': cls.SECRET
        }):
            cls.gateway = Gateway()

    def setUp(self):
        responses.start()
        responses.add(responses.POST,
                      f"{self.BASE_URL}/organizations/{self.SHOP_ID}/products/",
                      json=GATEWAY_PRODUCT,
                      status=200)
        responses.add(responses.POST,
                      f"{self.BASE_URL}/dashboard/webshops/{self.SHOP_ID}/products",
                      json={},
                      status=200)
        responses.add(responses.POST,
                      f"{self.BASE_URL}/uploads/",
                      json={
                          "url": "http://dummy.com/",
                          "fields": {
                              "key": 'abc'
                          }
                      },
                      status=200)
        responses.add(responses.POST,
                      "http://dummy.com",
                      json={},
                      status=200)

    def tearDown(self):
        responses.stop()
        responses.reset()

    def test_can_build_token(self):
        EXPECTED_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzaG9wOmE1NDdkZTE4LTdhMWQtNDUwYi1hNTdiLWJiZjdmMTc3ZGI4NCIsIm9yZ2FuaXphdGlvbl9ndWlkIjoiYTU0N2RlMTgtN2ExZC00NTBiLWE1N2ItYmJmN2YxNzdkYjg0IiwiZ3JvdXBzIjpbInNob3BrZWVwZXIiXX0.qtkzVdLOEpG2KrLqYHGbHyNTCoNX_r8-_0krBXCMUMo'
        self.assertEqual(self.gateway.token, EXPECTED_TOKEN)

    def test_can_create_product(self):
        product = Product(name='abc', price=12)
        self.gateway.create_product(product)

    def test_can_upload_image(self):
        new_url = self.gateway.upload_image(b'abc')
        self.assertEqual(new_url, "http://dummy.com/abc")
