import base64
import json
import logging
import uuid

import requests
from gwio.models import tags
from jose import jwt

logger = logging.getLogger(__name__)


class Gateway:
    def __init__(self, BASE_URL, SHOP_ID, SECRET, IMAGE_URL_PREFIX):
        self.BASE_URL = BASE_URL
        self.SHOP_ID = SHOP_ID
        self.shop_guid = uuid.UUID(SHOP_ID)
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
            # TODO: Make this work over API.
            variant_tag = tags.Tags(type=tags.TagType.VARIANT, name=product_variants[0].name, owner=self.shop_guid)
            variant_tag.save()
        else:
            variant_tag = None

        for product in product_variants:
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
                "name": product.name,
                "images": product.images,
                "vat": "VAT23"
            }

            if product.description:
                payload["desc"] = product.description
            if product.description_short:
                payload["brief"] = product.description_short
            if product.sku:
                payload["sku"] = product.sku
            if variant_tag:
                payload["tags"] = [str(variant_tag.guid)]
                payload["data"] = dict(variants=product.variant_data)

            # create product
            response = self.session.post(f"{self.BASE_URL}/organizations/{self.SHOP_ID}/products/",
                                         json=payload)
            if response.status_code >= 400:
                with open(f'failed_{uuid.uuid4()}.json', 'w+') as f:
                    json.dump(payload, f)
                logger.fatal(response.text)
                continue
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
