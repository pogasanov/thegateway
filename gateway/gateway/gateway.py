import base64
import logging
import re
import uuid
from decimal import Decimal
from itertools import groupby

import requests
import simplejson as json
from gateway.models import Product
from gateway.utils import download_image
from jose import jwt

logger = logging.getLogger(__name__)


class Gateway:
    def __init__(self, BASE_URL, SHOP_ID, SECRET, IMAGE_URL_PREFIX):
        self.BASE_URL = BASE_URL
        self.SHOP_ID = SHOP_ID
        self.shop_guid = uuid.UUID(SHOP_ID)
        self.SECRET = SECRET
        self.image_prefix = IMAGE_URL_PREFIX

        self.ENDPOINTS = self._generate_endpoints(self.BASE_URL, self.SHOP_ID)

        self.token = self._build_token()
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        self.tags_in_db = None

    @staticmethod
    def _generate_endpoints(base_url, shop_id):
        return {
            "product": {
                "list": f"{base_url}/dashboard/webshop_products/_query",
                "create": f"{base_url}/dashboard/webshops/{shop_id}/products",
                "delete": f"{base_url}/dashboard/webshops/{shop_id}/products/{{}}/",
            },
            "organization": {"product": {"delete": f"{base_url}/organizations/{shop_id}/products/{{}}/"}},
            "tag": {
                "list": f"{base_url}/webshops/{shop_id}/tags/",
                "create": f"{base_url}/webshops/{shop_id}/tags/",
                "delete": f"{base_url}/webshops/{shop_id}/tags/{{}}/",
            },
            "image": {"upload": f"{base_url}/uploads/"},
        }

    def _build_token(self):
        shop_guid = uuid.UUID(self.SHOP_ID)
        key = base64.b64decode(self.SECRET)
        return jwt.encode(
            dict(iss=f"shop:{shop_guid}", organization_guid=str(shop_guid), groups=["shopkeeper"],),
            key,
            algorithm="HS256",
        )

    @staticmethod
    def _log_failed(data, response):
        with open(f"failed_{uuid.uuid4()}.json", "w+") as f:
            json.dump(data, f, use_decimal=True)
        logger.fatal(response.text)

    def list_of_products(self):
        fetched = self._fetch_products()

        constructed = list()
        for product in fetched:
            constructed.append(
                Product(
                    name=product["name"],
                    price=Decimal(product["price"]["base"]["unit"]["amount"]),
                    stock=Decimal(product["stock_level"]),
                    description=product["desc"],
                    description_short=product["brief"],
                    sku=product["sku"],
                    images=[download_image(url, default_filename=product["name"]) for url in product["images"]],
                    variant_data=product["data"]["variants"] if product["data"] else [],
                )
            )

        grouped = list()
        for _, grouped_products in groupby(constructed, lambda x: x.name):
            grouped.append(list(grouped_products))
        return grouped

    def _fetch_products(self):
        response = self.session.post(
            self.ENDPOINTS["product"]["list"],
            json={
                "dsl": {
                    "size": 100,
                    "sort": [{"timestamps.created": "desc"}, {"guid": "asc"}],
                    "query": {
                        "bool": {
                            "must": [{"match": {"owner_guid": self.SHOP_ID}}],
                            "must_not": [{"exists": {"field": "archived"}}],
                        }
                    },
                }
            },
        )
        return response.json()["products"]

    def create_products(self, product_variants):
        if len(product_variants) > 1:
            variant_tag = self.create_tag(product_variants[0].name)
            if not variant_tag:
                return
        else:
            variant_tag = None

        payloads = list()
        for product in product_variants:
            payload = {"archived": False, "for_sale": True}
            product_data = {
                "base_price_type": "retail",
                "cost_price": {"currency": "zł", "vat_percent": 0, "amount": 0},
                "base_price": {"currency": "zł", "vat_percent": product.vat_percent, "amount": product.price,},
                "name": product.name,
                "vat": f"VAT{product.vat_percent}",
                "images": [self.upload_image(image) for image in product.images],
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

            payload["product"] = product_data
            # create product
            if product.stock:
                payload["stock_level"] = product.stock
            payloads.append(payload)

        data = {"products": payloads}
        response = self.session.post(self.ENDPOINTS["product"]["create"], json=data)
        if response.status_code >= 400:
            self._log_failed(data, response)

    def delete_all_products(self):
        products = self._fetch_products()
        for product in products:
            self.delete_product_by_id(product["guid"])

    def delete_product_by_id(self, id):
        self.session.delete(self.ENDPOINTS["product"]["delete"].format(id))
        self.session.delete(self.ENDPOINTS["organization"]["product"]["delete"].format(id))

    def list_of_tags(self):
        response = self.session.get(self.ENDPOINTS["tag"]["list"])
        return response.json()

    def create_tag(self, name: str):
        tag = self._get_tag(name)
        if tag:
            return tag["guid"]
        data = {"name": name, "type": "variant"}
        response = self.session.post(self.ENDPOINTS["tag"]["create"], json=data)
        if response.status_code == 409:
            return self._get_tag_guid_from_conflict_message(response.json()["message"])
        if response.status_code >= 400:
            self._log_failed(data, response)
            return None
        return response.json()["guid"]

    def _get_tag(self, name):
        if not self.tags_in_db:
            self.tags_in_db = self.list_of_tags()
        for tag in self.tags_in_db:
            if tag["name"] == name:
                return tag

    @staticmethod
    def _get_tag_guid_from_conflict_message(message: str):
        return re.search(r"\((.*)\)", message).group(1)

    def delete_all_tags(self):
        tags = self.list_of_tags()
        for tag in tags:
            self.delete_tag_by_id(tag["guid"])

    def delete_tag_by_id(self, id):
        self.session.delete(self.ENDPOINTS["tag"]["delete"].format(id))

    def upload_image(self, image_content):
        response = self.session.post(
            self.ENDPOINTS["image"]["upload"],
            json={"filename": image_content.filename, "content_type": image_content.mimetype,},
        )
        response.raise_for_status()

        url = response.json()["url"]
        fields = response.json()["fields"]

        response = requests.post(url, fields, files={"file": (image_content.filename, image_content.data)})
        response.raise_for_status()

        return url + fields["key"]
