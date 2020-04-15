import decimal
import logging

from json import JSONDecodeError
from typing import List, Dict, Generator

import requests

from gateway.models import Product, Image
from gateway.utils import download_image


# pylint: disable=invalid-name
from requests import Response

logger = logging.getLogger(__name__)


class Shoper:
    def __init__(self, base_url: str, username: str, password: str, translation_prefix: str = "pl_PL"):
        self.api_hostname = base_url
        self.username = username
        self.password = password
        self.translation_prefix = translation_prefix
        self.auth_token = self.authorize()
        self.taxes = self.get_taxes()

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

    def invoke(self, endpoint: str, method: str, output_format: str = None, stream: bool = False) -> Response:
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
        )

    def get_image(self, data: Dict) -> Image:
        filename = data.get("main_image").get("unic_name")
        image_url = f"{self.api_hostname}/userdata/public/gfx/{filename}.jpg"
        image = download_image(image_url)
        return image

    @staticmethod
    def _tax_dict(taxes: List[Dict]) -> Dict:
        return {tax.get("tax_id"): tax.get("value") for tax in taxes}

    def get_taxes(self) -> Dict:
        taxes_response = self.get("taxes")
        taxes = self._tax_dict(taxes_response.get("list"))
        return taxes

    def _categories_dict(self, categories: List[Dict]) -> Dict:
        return {
            category.get("category_id"): category.get("translations").get(self.translation_prefix).get("name")
            for category in categories
        }

    def get_categories(self) -> Dict:
        categories_response = self.get("categories")
        categories = self._categories_dict(categories_response.get("list"))
        return categories

    def get_product_data(self, data: Dict, option: str = "", options_count: int = 1) -> Product:
        images = [self.get_image(data)]

        # get values for variants
        stock = decimal.Decimal(data.get("stock").get("stock"))

        # if there are variants then distribute the stock number among the variants
        # that's probably a temporary solution
        if options_count > 1:
            stock = round(stock / options_count)

        sku = f"{data.get('stock').get('code')}_r{option}" if option else data.get("stock").get("code")

        translation = data.get("translations").get(self.translation_prefix)

        product = Product(
            name=translation.get("name"),
            price=data.get("stock").get("price"),
            stock=stock,
            description=translation.get("description"),
            sku=sku,
            description_short=translation.get("short_description"),
            variant_data={"size": option} if option else dict(),
            images=images,
            vat_percent=self.taxes.get(data.get("tax_id")),
        )

        return product

    def load_one_page(self, products_response: Dict) -> Generator[List, None, None]:
        for product in products_response.get("list"):
            if product.get("options"):
                # creates variants based on options
                options_number = len(product.get("options"))
                yield [self.get_product_data(product, option, options_number) for option in product.get("options")]
            else:
                yield [self.get_product_data(product)]

    def fetch_products(self) -> Generator[List, None, None]:
        """
        https://developers.shoper.pl/developers/api/resources/products/list
        There's a limit on a number of products on a page and it's maximum is 50 (default 10).
        Set it to 50 to make less API calls.
        """
        page_limit = 50
        products_response = self.get(f"products?limit={page_limit}")

        if products_response.get("pages") > 1:
            for i in range(2, products_response.get("pages")):
                products_response = self.get(f"products?limit={page_limit}&page={i}")
                return self.load_one_page(products_response)
        else:
            return self.load_one_page(products_response)