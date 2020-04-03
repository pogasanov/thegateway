import base64
import logging
import re
import uuid

import requests
import simplejson as json
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
        self.tags_in_db = self._get_tags_in_db()

    def _build_token(self):
        shop_guid = uuid.UUID(self.SHOP_ID)
        key = base64.b64decode(self.SECRET)
        return jwt.encode(
            dict(iss=f"shop:{shop_guid}",
                 organization_guid=str(shop_guid),
                 groups=['shopkeeper']
                 ), key, algorithm="HS256")

    def _get_tags_in_db(self):
        response = self.session.get(f"{self.BASE_URL}/webshops/{self.SHOP_ID}/tags/")
        return response.json()

    @staticmethod
    def _log_failed(data, response):
        with open(f'failed_{uuid.uuid4()}.json', 'w+') as f:
            json.dump(data, f, use_decimal=True)
        logger.fatal(response.text)

    def _get_tag(self, name):
        for tag in self.tags_in_db:
            if tag["name"] == name:
                return tag

    @staticmethod
    def _get_tag_guid_from_conflict_message(message: str):
        return re.search(r"\((.*)\)", message).group(1)

    def _create_tag(self, name: str):
        tag = self._get_tag(name)
        if tag:
            return tag["guid"]
        data = {
            "name": name,
            "type": "variant"
        }
        response = self.session.post(
            f"{self.BASE_URL}/webshops/{self.SHOP_ID}/tags/",
            json=data
        )
        if response.status_code == 409:
            return self._get_tag_guid_from_conflict_message(response.json()["message"])
        if response.status_code >= 400:
            self._log_failed(data, response)
            return None
        return response.json()["guid"]

    def create_product(self, product_variants):
        if len(product_variants) > 1:
            variant_tag = self._create_tag(product_variants[0].name)
            if not variant_tag:
                return
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
                        "vat_percent": product.vat_percent,
                        "amount": product.price
                    },
                "name": product.name,
                "images": product.images,
                "vat": f"VAT{product.vat_percent}",
            }

            if product.description:
                product_data["desc"] = product.description
            if product.description_short:
                product_data["brief"] = product.description_short
            if product.sku:
                product_data["sku"] = product.sku
            if variant_tag:
                product_data["tag_guids"] = [variant_tag]
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
            self._log_failed(data, response)

    def upload_image(self, image_content):
        """
        TODO: Rewrite this - you get the file as a stream from the /images/products/{product_id}/{image_id} so you can upload them without temp files if
        you do the uploads call and subsequent S3 call with the utils.io.StreamResponse to the presigned url returned by GW API /uploads/
        bucket.put_object(
            Body=stream,
            Key=key_,
            ContentType=content_type,
            Metadata=dict(
                original_url=url,
            ),
        )
        """
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
