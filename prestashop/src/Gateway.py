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
        image_urls = [self.upload_image(image) for image in product.images]

        payload = {
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
            "name": product.name,
            "images": image_urls,
            "vat": "VAT23"
        }

        if product.description:
            payload["desc"] = product.description
        if product.description_short:
            payload["brief"] = product.description_short
        if product.sku:
            payload["sku"] = product.sku

        # create product
        response = self.session.post(f"{self.BASE_URL}/organizations/{self.SHOP_ID}/products/",
                                     json=payload)
        product_guid = response.json()['guid']

        payload = {
            "product_guid": product_guid,
            "archived": False,
            "for_sale": True
        }
        if product.stock:
            payload["stock_level"] = product.stock
        # add product to webshop
        self.session.post(f"{self.BASE_URL}/dashboard/webshops/{self.SHOP_ID}/products",
                          json={
                              "products": [
                                  payload
                              ]})

    def upload_image(self, image_content):
        response = self.session.post(f"{self.BASE_URL}/uploads/",
                                     json={
                                         "filename": "product_image.jpg",
                                         "content_type": "image/jpeg"
                                     })

        url = response.json()['url']
        fields = response.json()['fields']

        requests.post(url, fields, files={
            'file': ('file.jpg', image_content)
        })
        return url + fields['key']
