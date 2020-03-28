import base64
import os
import uuid

import requests
from jose import jwt


class Gateway:
    def __init__(self):
        self.BASE_URL = os.environ.get('GATEWAY_BASE_URL', 'https://sma.dev.gwapi.eu')
        self.SHOP_ID = os.environ.get('GATEWAY_SHOP_ID', 'a547de18-7a1d-450b-a57b-bbf7f177db84')
        self.SECRET = os.environ.get('GATEWAY_SECRET', 'OyB2YbwTVtRXuJv+VE4oJLVyGo8pf1XVibCk08lt4ys=')

        self.token = self._build_token()
        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'Bearer {self.token}'})

    def _build_token(self):
        shop_guid = uuid.UUID(self.SHOP_ID)
        key = base64.b64decode(self.SECRET)
        return jwt.encode(
            dict(iss=f"shop:{shop_guid}",
                 organization_guid=str(shop_guid),
                 groups=['shopkeeper']
                 ), key, algorithm="HS256")

    def create_product(self, product):
        # create product
        response = self.session.post(f"{self.BASE_URL}/organizations/{self.SHOP_ID}/products/",
                                     json={
                                         "base_price_type": "retail",
                                         "cost_price":
                                             {
                                                 "currency": "zł",
                                                 "vat_percent": 0,
                                                 "amount": 0
                                             },
                                         "base_price":
                                             {
                                                 "currency": "zł",
                                                 "vat_percent": 23,
                                                 "amount": product.price
                                             }, "tags": [],
                                         "data":
                                             {
                                                 "imageFiles": [],
                                                 "videos": [],
                                                 "fit": "d",
                                                 "returns": "e",
                                                 "fabric": "f"
                                             },
                                         "desc": product.description,
                                         "brief": product.description_short,
                                         "sku": product.sku,
                                         "name": product.name,
                                         "images": [],
                                         "vat": "VAT23"
                                     })
        product_guid = response.json()['guid']

        # add product to webshop
        self.session.post(f"{self.BASE_URL}/dashboard/webshops/{self.SHOP_ID}/products",
                          json={
                              "products": [
                                  {
                                      "product_guid": product_guid,
                                      "stock_level": product.stock,
                                      "archived": False,
                                      "for_sale": True
                                  }
                              ]})
