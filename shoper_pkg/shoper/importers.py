import decimal
import json
import logging
import urllib
from json import JSONDecodeError
from typing import (
    Dict,
    Generator,
    List,
)

import requests
from gateway import Gateway
from gateway.models import Product
# pylint: disable=invalid-name
from requests import Response

logger = logging.getLogger(__name__)


class Shoper:
    def __init__(
            self,
            base_url: str,
            username: str,
            password: str,
            exporter: Gateway,
            translation_prefix: str = "pl_PL",
            stock_update: bool = True,
    ):
        self.api_hostname = base_url
        self.username = username
        self.password = password
        self.translation_prefix = translation_prefix
        self.auth_token = self.authorize()
        if not stock_update:
            self.taxes = self.get_taxes()
        self.exporter = exporter
        self.mapped_categories = {}
        self.categories_dict = dict()
        self._gw_categories = None

    @property
    def category_mapping_filename(self):
        return f'category_mappings_{urllib.parse.urlparse(self.api_hostname).netloc.replace(".", "_")}'

    def authorize(self) -> str:
        response = requests.post(
            f"{self.api_hostname}/webapi/rest/auth", data={"client_id": self.username, "client_secret": self.password}
        )
        return response.json().get("access_token")

    def head(self, endpoint: str) -> Response:
        return self.invoke(endpoint, "head")

    def get(self, endpoint: str, output_format: str = "JSON") -> Dict:
        response = self.invoke(endpoint, "get", output_format)
        try:
            return response.json()
        except JSONDecodeError:
            # pylint: disable=logging-format-interpolation
            logger.fatal(f"{response.status_code}: {response.text}")
            raise

    def put(self, endpoint: str, data: Dict, output_format: str = "JSON") -> Dict:
        response = self.invoke(endpoint, "put", output_format, data=data)
        try:
            if not response.status_code == 200:
                logger.critical(response.json())
            return response.json()
        except JSONDecodeError:
            # pylint: disable=logging-format-interpolation
            logger.fatal(f"{response.status_code}: {response.text}")
            raise

    def invoke(
            self, endpoint: str, method: str, output_format: str = None, stream: bool = False, data: Dict = None
    ) -> Response:
        # pylint: disable=invalid-name
        fn = getattr(requests, method)
        if output_format:
            params = dict(output_format=output_format)
        else:
            params = dict()
        return fn(
            f"{self.api_hostname}/webapi/rest/{endpoint}",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            params=params,
            stream=stream,
            data=data,
        )

    def get_image_url(self, data: Dict) -> str:
        filename = data.get("main_image").get("unic_name")
        image_url = f"{self.api_hostname}/userdata/public/gfx/{filename}.jpg"
        return image_url

    @staticmethod
    def _tax_dict(taxes: List[Dict]) -> Dict:
        return {tax.get("tax_id"): tax.get("value") for tax in taxes}

    def get_taxes(self) -> Dict:
        taxes_response = self.get("taxes")
        taxes = self._tax_dict(taxes_response.get("list"))
        return taxes

    def _get_categories(self, product):
        mappings = self.exporter.get_category_mappings('..', self.category_mapping_filename)

        try:
            orig_categories = [mappings[str(category)] for category in product['categories']]
        except KeyError as e:
            raise ValueError(f'Missing category mapping for category: {e}') from e
        if self._gw_categories is None:
            self._gw_categories = {t['name'].lower(): t['guid'] for t in self.exporter.list_of_tags(type='category')}

        category_guids = []
        for oc in orig_categories:
            for gwc in oc['categories']:
                try:
                    category_guids.append(self._gw_categories[gwc.lower()])
                except KeyError:
                    raise ValueError(f'No category tag with name `{gwc}`')
        return category_guids

    def get_product_data(self, data: Dict, option: str = "", options_count: int = 1) -> Product:
        images = [self.get_image_url(data)] if data.get("main_image") else None

        # get values for variants
        stock = decimal.Decimal(data.get("stock").get("stock"))

        # if there are variants then distribute the stock number among the variants
        # that's probably a temporary solution
        if options_count > 1:
            stock = round(stock / options_count)

        sku = f"{data.get('stock').get('code')}_r{option}" if option else data.get("stock").get("code")

        translation = data.get("translations").get(self.translation_prefix)

        category_guids = self._get_categories(product=data)

        product = Product(
            name=translation.get("name"),
            price=data.get("stock").get("price"),
            stock=stock,
            description=translation.get("description"),
            sku=sku,
            description_short=translation.get("short_description"),
            variant_data={"size": str(option)} if option else dict(),
            images_urls=images,
            vat_percent=self.taxes.get(data.get("tax_id")),
            tag_guids=set(category_guids),
        )

        return product

    def load_product_list(self, product: Dict) -> List[Product]:
        if product.get("options"):
            # creates variants based on options
            options_number = len(product.get("options"))
            return [self.get_product_data(product, option, options_number) for option in product.get("options")]
        return [self.get_product_data(product)]

    def fetch_products(self) -> Generator[List, None, None]:
        """
        https://developers.shoper.pl/developers/api/resources/products/list
        There's a limit on a number of products on a page and it's maximum is 50 (default 10).
        Set it to 50 to make less API calls.
        """
        self.check_categories_are_mapped()
        self.exporter.check_mapped_categories(self.category_mapping_filename)

        page_limit = 50
        products_response = self.get(f"products?limit={page_limit}")

        # Load first page
        for product in products_response.get("list"):
            yield self.load_product_list(product)
        # If there are more pages of data then load more products
        if products_response.get("pages") > 1:
            for i in range(2, products_response.get("pages")):
                products_response = self.get(f"products?limit={page_limit}&page={i}")
                for product in products_response.get("list"):
                    yield self.load_product_list(product)

    def fetch_product(self, product: Product) -> Dict:
        page_limit = 1
        sku = product.sku.split("_")[0]
        code_filter = json.dumps({"stock.code": sku})
        products_response = self.get(f"products?limit={page_limit}&filters={code_filter}")
        if int(products_response.get("count")) > 1:
            # pylint: disable=logging-format-interpolation
            logger.error(f"error: Found {products_response.get('count')} products with code {sku}")
            raise
        return products_response.get("list")[0]

    def get_stock_for_single_product(self, product: Product) -> int:
        product_data = self.fetch_product(product)
        return product_data.get("stock").get("stock")

    def update_product_stock(self, product: Product) -> Dict:
        """
        Filtering by code is only possible on list endpoint.
        Page limit set to 1 cause even if there are, somehow,
        more products, there's no reason to show them.
        """
        product_to_update = self.fetch_product(product)
        return self.put(
            f"products/{product_to_update.get('product_id')}", json.dumps({"stock": {"stock": product.stock}})
        )

    def get_categories(self):
        categories_response = self.get("categories")
        category_objects = categories_response.get("list")
        categories = {category.get("category_id"): category.get("translations").get(self.translation_prefix).get("name") for category in category_objects}
        while categories_response['page'] < categories_response['pages']:
            categories_response = self.get(f"categories?page={categories_response['page'] + 1}")
            category_objects = categories_response.get("list")
            categories.update(
                {category.get("category_id"): category.get("translations").get(self.translation_prefix).get("name") for category in category_objects}
            )
        return categories

    def check_categories_are_mapped(self):
        mappings = self.exporter.get_category_mappings('..', self.category_mapping_filename)
        errors = dict()
        for category_id, category_name in self.get_categories().items():
            if str(category_id) not in mappings.keys():
                errors[category_id] = category_name
        if errors:
            raise NotImplementedError(f'Missing mapping for categories: {errors}')
