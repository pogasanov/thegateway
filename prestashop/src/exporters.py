import base64
import logging
import uuid

import requests
import simplejson as json
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
        payloads = list()
        for product in product_variants:
            payload = {
                "archived": False,
                "for_sale": True
            }
            product_data = {
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
                    },
                "name": product.name,
                "images": product.images,
                "vat": "VAT23",
            }

            if product.description:
                product_data["desc"] = product.description
            if product.description_short:
                product_data["brief"] = product.description_short
            if product.sku:
                product_data["sku"] = product.sku
            if variant_tag:
                product_data["tag_guids"] = [str(variant_tag.guid)]
                product_data["data"] = dict(variants=product.variant_data)

            payload['product'] = product_data
            # create product
            if product.stock:
                payload["stock_level"] = product.stock
            payloads.append(payload)

        data = {"products": payloads}
        response = self.session.post(f"{self.BASE_URL}/dashboard/webshops/{self.SHOP_ID}/products",
                                     json=data)
        if response.status_code >= 400:
            with open(f'failed_{uuid.uuid4()}.json', 'w+') as f:
                json.dump(data, f, use_decimal=True)
            logger.fatal(response.text)

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
