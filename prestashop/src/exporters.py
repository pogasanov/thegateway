import base64
import uuid

import requests
from jose import jwt


class Gateway:
    def __init__(self, BASE_URL, SHOP_ID, SECRET, IMAGE_URL_PREFIX):
        self.BASE_URL = BASE_URL
        self.SHOP_ID = SHOP_ID
        self.SECRET = SECRET
        self.image_prefix = IMAGE_URL_PREFIX

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

    def create_product(self, product_variants):
        if len(product_variants) > 1:
            # TODO: Check length of product_variants list - if multiple, create variant tag and tag all product_variants with it, otherwise just do the following.
            raise NotImplemented
        else:
            product = product_variants[0]

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
            "images": [f'{self.image_prefix}/{url}' for url in image_urls],
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
