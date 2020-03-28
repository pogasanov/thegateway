import os
from unittest import TestCase, mock

import responses

from prestashop.src.Gateway import Gateway
from prestashop.src.Product import Product

GATEWAY_PRODUCT = {
    "activated": None,
    "brief": None,
    "created": "2020-03-28T08:15:07.587983+00:00",
    "data": {
        "imageFiles": [],
        "videos": []
    },
    "desc": None,
    "guid": "9fea73c7-2be4-4f6c-903c-10cbac9dbeb5",
    "images": [],
    "name": "test23",
    "owner_guid": "a547de18-7a1d-450b-a57b-bbf7f177db84",
    "price": {
        "currency": "zł",
        "final": {
            "unit": {
                "amount": 1.00,
                "currency": "zł",
                "vat": 0.19,
                "vat0": 0.81,
                "vat_percent": 23
            }
        },
        "original": {
            "campaign_modifier": None,
            "unit": {
                "amount": 1.00,
                "currency": "zł",
                "vat": 0.19,
                "vat0": 0.81,
                "vat_percent": 23
            }
        },
        "vat_class": 23
    },
    "pricing": None,
    "size": None,
    "sku": None,
    "tag_guids": [],
    "tags": [],
    "timestamps": {
        "created": "2020-03-28T08:15:08.730176+00:00"
    },
    "type": "default",
    "vat": "VAT23",
    "weight": None
}


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

    def test_can_build_token(self):
        EXPECTED_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzaG9wOmE1NDdkZTE4LTdhMWQtNDUwYi1hNTdiLWJiZjdmMTc3ZGI4NCIsIm9yZ2FuaXphdGlvbl9ndWlkIjoiYTU0N2RlMTgtN2ExZC00NTBiLWE1N2ItYmJmN2YxNzdkYjg0IiwiZ3JvdXBzIjpbInNob3BrZWVwZXIiXX0.qtkzVdLOEpG2KrLqYHGbHyNTCoNX_r8-_0krBXCMUMo'
        self.assertEqual(self.gateway.token, EXPECTED_TOKEN)

    @responses.activate
    def test_can_create_product(self):
        responses.add(responses.POST,
                      f"{self.BASE_URL}/organizations/{self.SHOP_ID}/products/",
                      json=GATEWAY_PRODUCT,
                      status=200)
        responses.add(responses.POST,
                      f"{self.BASE_URL}/dashboard/webshops/{self.SHOP_ID}/products",
                      json={},
                      status=200)
        product = Product(name='abc', price=12)
        self.gateway.create_product(product)
