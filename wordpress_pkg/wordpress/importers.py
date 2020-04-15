import logging
from typing import List

from woocommerce import API

CONSUMER_KEY = ""
CONSUMER_SECRET = ""
BASE_URL = ""
logger = logging.getLogger(__name__)


class WordPressWooCommerce:
    def __init__(self, consumer_key: str, consumer_secret: str, base_url: str):
        self.wcapi = API(url=base_url, consumer_key=consumer_key, consumer_secret=consumer_secret)

    def _get_variants_of_product(self, product: dict):
        pass

    def _fetch_products_from_api(self) -> List[dict]:
        response = self.wcapi.get("products")
        if response.status_code == 401:
            logger.error("Invalid credentials (code 401)")
            return []

        if response.status_code == 404:
            logger.error("Invalid url or invalid permalinks (https://stackoverflow.com/a/46326542)")
            return []

        if response.status_code != 200:
            logger.error("Error occurred (code %s)", response.status_code)
            return []

        return response.json()

    def get_products(self):
        api_products = self._fetch_products_from_api()
