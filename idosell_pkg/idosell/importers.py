import json
import logging
import xml.etree.ElementTree as ET
from datetime import date
from decimal import Decimal
from hashlib import sha1
from typing import (
    Iterator,
    List,
)
from urllib.parse import urlparse

import requests
from gateway.models import Product

# pylint: disable=C0103
logger = logging.getLogger(__name__)


class IdoSell:
    LANGUAGE = "pol"
    NAMESPACES = {"xml": "http://www.w3.org/XML/1998/namespace"}

    STOCK_UNAVAILABLE = "unavailable"
    STOCK_UNKNOWN_AVAILABLE_QUANTITY = "-1"
    """
    Inside every product there are 'size' tags
    this name is misleading, because
    it not always contains size of product as the name suggests
    """
    GUARANTEED_VARIANT_TAG = "size"
    GW_PRODUCT_UNKNOWN_QUANTITY = Decimal("100001")

    def __init__(self, login: str, password: str, base_url: str):
        self.login = login
        self.password = password
        self.url = base_url + "/marketplace-api/?gate=Products/getProductsFeed/5/json"

        self.exporter = None

        self.__products_xml = None

    @property
    def category_mapping_filename(self):
        return f'category_mappings_{urlparse(self.url).netloc.replace(".", "_")}'

    @property
    def products_xml(self):
        if self.__products_xml is None:
            self.__products_xml = self._get_xml_with_products()
        return self.__products_xml

    @staticmethod
    def _set_xml_lang(xpath: str):
        """
        Some tags have possibility to have content in more than one language,
        making sure that we get elements only in provided language
        """
        lang_parameter = f"@xml:lang='{IdoSell.LANGUAGE}'"
        return xpath.format(lang=lang_parameter)

    @staticmethod
    def _find(el: ET.Element, xpath: str, lang=False) -> ET.Element:
        """
             Helping method for fetching information from xml
        """
        if lang:
            xpath = IdoSell._set_xml_lang(xpath)
        return el.find(xpath, namespaces=IdoSell.NAMESPACES)

    @staticmethod
    def _findall(el: ET.Element, xpath: str, lang=False) -> List[ET.Element]:
        """
             Helping method for fetching information from xml
        """
        if lang:
            xpath = IdoSell._set_xml_lang(xpath)
        return el.findall(xpath, namespaces=IdoSell.NAMESPACES)

    def _get_product(self, xml_product: ET.Element) -> dict:
        """
            Fetch product from product xml tag
        """
        product = dict()

        product["name"] = self._find(xml_product, "./description/name[{lang}]", lang=True).text
        product["vat"] = float(xml_product.attrib["vat"])

        brief_description = self._find(xml_product, "./description/short_desc[{lang}]", lang=True)
        product["brief"] = brief_description.text.strip() if brief_description is not None else ""

        product["image_urls"] = self._get_image_urls(xml_product)
        product["category"] = self._find(xml_product, "./category").attrib
        product["variant_data"] = dict()
        product["sku"] = xml_product.attrib["id"]

        product["variant_data"][self.GUARANTEED_VARIANT_TAG] = self._get_sizes(xml_product)

        xml_group = xml_product.find("./group")
        if xml_group:
            # if the products have its unique ID, but common attribute
            # we can unify them by setting the same ID
            product["sku"] = xml_group.attrib["first_product_id"]
            xml_groups = xml_group.findall("./group_by_parameter")
            for xml_group_by_parameter in xml_groups:
                group_name = self._find(xml_group_by_parameter, "./name[{lang}]", lang=True).text.lower()
                product["variant_data"][group_name] = set()
                product["variant_data"][group_name].add(
                    self._find(xml_group_by_parameter, "./product_value/name", lang=True).text.lower()
                )

        xml_parameters = xml_product.find("./parameters")
        if xml_parameters:
            for xml_parameter in self._findall(xml_parameters, "./parameter[{lang}]", lang=True):
                group_name = xml_parameter.attrib["name"].lower()
                param_values = product["variant_data"].get(group_name, set())

                for xml_value in self._findall(xml_parameter, "./value[{lang}]", lang=True):
                    param_values.add(xml_value.attrib["name"].lower())

                product["variant_data"][group_name] = param_values

        return product

    # pylint: disable=R0201
    def _get_image_urls(self, xml_product: ET) -> list:
        """
        Get urls of images from product xml element tree
        """
        images = []
        for xml_image in xml_product.findall("./images/large/"):
            images.append(xml_image.attrib["url"])

        return images

    def _get_sizes(self, xml_product: ET) -> List[dict]:
        """
        Get variants from sizes tag
        name: str
        price: Decimal
        stock: Decimal
        """
        sizes = []
        xml_sizes = xml_product.findall("./sizes/size")
        for xml_variant in xml_sizes:
            size = dict()
            if "name" in xml_variant.attrib:
                size["name"] = xml_variant.attrib["name"]
            else:
                size["name"] = xml_variant.attrib["panel_name"]

            size["price"] = Decimal(xml_variant.find("./price").attrib["net"])
            stock_availability = xml_variant.attrib["available"]
            if stock_availability == "unavailable":
                stock = Decimal("0")
            else:
                xml_stocks = xml_variant.findall("./stock")
                stock = Decimal("0")
                for xml_stock in xml_stocks:
                    if xml_stock.attrib["available_stock_quantity"] == self.STOCK_UNKNOWN_AVAILABLE_QUANTITY:
                        # special case, not given information how many products available
                        # needs to be handled in the future
                        stock = self.GW_PRODUCT_UNKNOWN_QUANTITY
                        break
                    stock += Decimal(xml_stock.attrib["available_stock_quantity"])

            size["stock"] = stock
            sizes.append(size)

        return sizes

    def _get_tag_guids(self, category):
        mappings = self.exporter.get_category_mappings(self.category_mapping_filename)

        tag_guids = set()
        for mapped_name in mappings[category['id']]['categories']:
            tag_guids.add(self.exporter.get_category_id_by_name(mapped_name, category["id"]))

        return tag_guids

    def _convert_fetched_product_to_gateway_products(self, fetched_product: dict) -> List[Product]:
        product_template = dict()
        product_template["name"] = fetched_product["name"]
        product_template["category"] = fetched_product["category"]
        product_template["vat_percent"] = fetched_product["vat"]
        product_template["description_short"] = fetched_product["brief"]
        product_template["sku"] = fetched_product["sku"]
        product_template["images_urls"] = fetched_product["image_urls"]
        return self._create_gateway_products_from_variants(product_template, fetched_product["variant_data"])

    def _create_gateway_products_from_variants(self, product_template: dict, variants: dict) -> List[Product]:
        """
        Method for helping creating products as gateway product model
        """
        sizes = variants.pop(self.GUARANTEED_VARIANT_TAG)
        created_gw_products = []
        for size in sizes:
            gw_prod = Product(
                name=product_template["name"],
                price=size["price"],
                vat_percent=product_template["vat_percent"],
                tag_guids=self._get_tag_guids(product_template.get("category")),
            )
            gw_prod.description_short = product_template["description_short"]
            gw_prod.sku = product_template["sku"]
            gw_prod.images_urls = product_template["images_urls"]
            gw_prod.stock = size["stock"]
            gw_prod.variant_data = dict()
            gw_prod.variant_data["size"] = size["name"]
            for variant_name, variant_values in variants.items():
                if isinstance(variant_values, set):
                    gw_prod.variant_data[variant_name] = sorted(list(variant_values))
                else:
                    gw_prod.variant_data[variant_name] = variant_values

            created_gw_products.append(gw_prod)

        return created_gw_products

    # pylint: disable=R1710
    def get_products(self) -> Iterator[Iterator[Product]]:
        """
        Get product variants from IdoSell API as gateway product model
        """
        self.check_categories_are_mapped()
        self.exporter.check_mapped_categories(self.category_mapping_filename)
        xml_content = self.products_xml
        if not xml_content:
            return []
        xml_root = ET.fromstring(xml_content)
        xml_products = xml_root.findall("./products/product")
        total = len(xml_products)
        for index, xml_product in enumerate(xml_products, 1):
            print(f"{index}/{total}")
            product_variants = self._get_product(xml_product)
            yield self._convert_fetched_product_to_gateway_products(product_variants)

    def _generate_authorization_key(self):
        """
        Instruction for generating authorization key
        https://www.idosell.com/pl/shop/developers/api/faq/najczesciej-zadawane-pytania-dotyczace-api-pa-idosell-shop/#3
        """
        today = date.today()
        today = today.strftime("%Y%m%d")
        hashed_password = sha1(self.password.encode())
        hashed_password = hashed_password.hexdigest()
        key = sha1((str(today) + hashed_password).encode())
        return key.hexdigest()

    @staticmethod
    def response_contains_file(response: requests.Response) -> bool:
        return "html" not in response.headers["content-type"] and "attachment" in response.headers.get(
            "content-disposition", ""
        )

    def _get_xml_with_products(self):
        """
        In order to get needed data, we need to send three requests
            1. Send authorization data to get url with available files
            2. Send request to url (from above) to get list of available xml files
            3. Fetch url (from above xml response) and send request to get xml with products
        """
        key = self._generate_authorization_key()
        authorization_body = json.dumps({"authenticate": {"userLogin": self.login, "authenticateKey": key}})

        response = requests.get(self.url, data=authorization_body)
        response_json = response.json()
        if "errors" in response_json and response_json["errors"]["faultCode"] != 0:
            logging.error(
                "An error occured while logging into the Marketplace API '%s'", response_json["errors"]["faultString"],
            )
            return None

        files_url = response_json["results"]["url"]
        response_with_available_xml_files = requests.get(files_url)
        xml_full_tag = ET.fromstring(response_with_available_xml_files.text).find("full")
        file_url = xml_full_tag.attrib["url"]
        response_with_xml_file = requests.get(file_url)

        if self.response_contains_file(response_with_xml_file):
            return response_with_xml_file.text

        logging.error(
            "Marketplace API did not return an xml file "
            "(probably the file already has been downloaded within 60 minutes)"
        )
        return None

    def get_categories(self):
        xml_content = self.products_xml
        if not xml_content:
            return []

        xml_root = ET.fromstring(xml_content)
        xml_categories = xml_root.findall("./products/product/category")
        total = len(xml_categories)
        categories = {}
        for index, xml_category in enumerate(xml_categories, 1):
            print(f"{index}/{total}")
            categories[xml_category.attrib["id"]] = xml_category.attrib["name"]
        return categories

    def check_categories_are_mapped(self):
        mappings = self.exporter.get_category_mappings(self.category_mapping_filename)
        for category_id, category_name in self.get_categories().items():
            if str(category_id) not in mappings.keys():
                raise NotImplementedError(f'Missing mapping for category `{category_id}` ({category_name})')
