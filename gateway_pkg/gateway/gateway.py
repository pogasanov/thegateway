import base64
import csv
import logging
import re
import uuid
from decimal import Decimal
from itertools import groupby
from urllib import parse

import requests
import simplejson as json
from jose import jwt
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from .models import Product
from .utils import download_image

LOGGER = logging.getLogger(__name__)


class Gateway:
    def __init__(self, base_url, shop_id, secret):
        self.base_url = base_url
        self.shop_id = shop_id
        self.shop_guid = uuid.UUID(shop_id)
        self.endpoints = self._generate_endpoints(self.base_url, self.shop_id)
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=Retry(total=5, backoff_factor=0.5)))
        self.session.headers.update({"Authorization": f"Bearer {self._build_token(secret)}"})
        self.tags_in_db = None
        self._categories = None
        self.category_mappings = dict()

    @property
    def categories(self):
        if self._categories is None:
            self._categories = self.list_of_tags(type='category')
        return self._categories

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
                "list": f"{base_url}/tags/",
            },
            "webshop_tag": {
                "list": f"{base_url}/webshops/{shop_id}/tags/",
                "create": f"{base_url}/webshops/{shop_id}/tags/",
                "delete": f"{base_url}/webshops/{shop_id}/tags/{{}}/",
            },
            "image": {"upload": f"{base_url}/uploads/", "public_upload": f"{base_url}/downloads/"},
        }

    def _build_token(self, secret):
        shop_guid = uuid.UUID(self.shop_id)
        key = base64.b64decode(secret)
        return jwt.encode(
            dict(iss=f"shop:{shop_guid}", organization_guid=str(shop_guid), groups=["shopkeeper"], ),
            key,
            algorithm="HS256",
        )

    @staticmethod
    def _log_failed(data, response):
        with open(f"failed_{uuid.uuid4()}.json", "w+") as file:
            json.dump(data, file, use_decimal=True)
        LOGGER.fatal(response.text)

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
            self.endpoints["product"]["list"],
            json={
                "dsl": {
                    "size": 100,
                    "sort": [{"timestamps.created": "desc"}, {"guid": "asc"}],
                    "query": {
                        "bool": {
                            "must": [{"match": {"owner_guid": self.shop_id}}],
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
            payload = {"archived": False, "for_sale": product.for_sale}
            if product.images_urls:
                images = [self.upload_public_image(image_url) for image_url in product.images_urls]
            else:
                images = [self.upload_image(image) for image in product.images]
            product_data = {
                "base_price_type": "retail",
                "cost_price": {"currency": "zł", "vat_percent": 0, "amount": 0},
                "base_price": {"currency": "zł", "vat_percent": 0, "amount": product.price},
                "name": product.name,
                "vat": f"VAT{product.vat_percent}",
                "images": images,
                "tag_guids": list(product.tag_guids),
            }

            if product.description:
                product_data["desc"] = product.description
            if product.description_short:
                product_data["brief"] = product.description_short
            if product.sku:
                product_data["sku"] = product.sku
            if variant_tag:
                product_data["tag_guids"].append(variant_tag)
                product_data["data"] = dict(variants=product.variant_data)

            payload["product"] = product_data
            # create product
            if product.stock:
                payload["stock_level"] = product.stock
            payloads.append(payload)

        data = {"products": payloads}
        response = self.session.post(self.endpoints["product"]["create"], json=data)
        if response.status_code >= 400:
            self._log_failed(data, response)

    def delete_all_products(self):
        products = self._fetch_products()
        for product in products:
            self.delete_product_by_id(product["guid"])

    def delete_product_by_id(self, product_id):
        self.session.delete(self.endpoints["product"]["delete"].format(product_id))
        self.session.delete(self.endpoints["organization"]["product"]["delete"].format(product_id))

    def get_category_mappings(self, category_mapping_filename):
        try:
            return self.category_mappings[category_mapping_filename]
        except KeyError:
            mappings = dict()
            with open(f'{category_mapping_filename}.csv', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    categories = set()
                    for i in range(2, len(row)):
                        if row[i].strip():
                            categories.update(x.strip() for x in row[i].split('>'))
                    mappings[row[0]] = dict(
                        src_name=row[1],
                        categories=list(categories)
                    )

            self.category_mappings[category_mapping_filename] = mappings
            return self.category_mappings[category_mapping_filename]

    def list_of_tags(self, type=None):
        if type:
            response = self.session.get(f'{self.endpoints["tag"]["list"]}?type={type}')
        else:
            response = self.session.get(self.endpoints["tag"]["list"])
        return response.json()

    def get_category_id_by_name(self, name, identifier=None):
        errors = dict()
        try:
            return next(x['guid'] for x in self.categories if x['name'].lower() == name.lower())
        except StopIteration:
            errors[name] = identifier

        if errors:
            raise ValueError(f'Invalid mapped categories: {errors}')

    def check_mapped_categories(self, filename):
        mappings = self.get_category_mappings(filename)

        for integration_id, integration_category in mappings.items():
            for mapped_name in integration_category['categories']:
                self.get_category_id_by_name(mapped_name, integration_id)

    def create_tag(self, name: str):
        tag = self._get_tag(name)
        if tag:
            return tag["guid"]
        data = {"name": name, "type": "variant"}
        response = self.session.post(self.endpoints["webshop_tag"]["create"], json=data)
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
        return None

    @staticmethod
    def _get_tag_guid_from_conflict_message(message: str):
        return re.search(r"\((.*)\)", message).group(1)

    def delete_all_tags(self):
        tags = self.list_of_tags()
        for tag in tags:
            self.delete_tag_by_id(tag["guid"])

    def delete_tag_by_id(self, tag_id):
        self.session.delete(self.endpoints["webshop_tag"]["delete"].format(tag_id))

    def upload_image(self, image_content):
        response = self.session.post(
            self.endpoints["image"]["upload"],
            json={"filename": image_content.filename, "content_type": image_content.mimetype},
        )
        response.raise_for_status()

        url = response.json()["url"]
        fields = response.json()["fields"]
        retries = Retry(total=5, backoff_factor=0.5)
        session = requests.Session()
        session.mount("https://", HTTPAdapter(max_retries=retries))
        response = session.post(url, fields, files={"file": (image_content.filename, image_content.data)})
        response.raise_for_status()

        return url + fields["key"]

    @staticmethod
    def _escape_non_ascii_characters_in_url(url: str) -> str:
        """
        For example convert "http://example.com/Zdjęcie-1.jpg" to "http://example.com/Zdj%C4%99cie-1.jpg"
        """
        parsed_url = list(parse.urlsplit(url))
        parsed_url[2] = parse.quote(parsed_url[2])
        return parse.urlunsplit(parsed_url)

    def upload_public_image(self, image_url: str):
        if not image_url.isascii():
            image_url = self._escape_non_ascii_characters_in_url(image_url)
        response = self.session.post(self.endpoints["image"]["public_upload"], json={"url": image_url})
        return response.json()["url"]
