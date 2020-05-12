import logging
import os

import click
from gateway.gateway import Gateway
from wordpress.importers import WoocommerceWordPress

logger = logging.getLogger(__name__)

WOOCOMMERCE_CONSUMER_KEY = os.environ.get("WOOCOMMERCE_CONSUMER_KEY")
WOOCOMMERCE_CONSUMER_SECRET = os.environ.get("WOOCOMMERCE_CONSUMER_SECRET")
WOOCOMMERCE_BASE_URL = os.environ.get("WOOCOMMERCE_BASE_URL")

importer = WoocommerceWordPress(WOOCOMMERCE_CONSUMER_KEY, WOOCOMMERCE_CONSUMER_SECRET, WOOCOMMERCE_BASE_URL)

GATEWAY_BASE_URL = os.environ.get("GATEWAY_BASE_URL")
GATEWAY_SHOP_ID = os.environ.get("GATEWAY_SHOP_ID")
GATEWAY_SECRET = os.environ.get("GATEWAY_SECRET")
IMAGE_URL_PREFIX = f"{os.environ.get('IMAGEBUCKET_URL')}{GATEWAY_SHOP_ID}/"


@click.command()
def run_import():
    print(WOOCOMMERCE_CONSUMER_KEY)
    exporter = Gateway(GATEWAY_BASE_URL, GATEWAY_SHOP_ID, GATEWAY_SECRET, IMAGE_URL_PREFIX)
    importer.exporter = exporter

    for product_variants in importer.get_products():
        exporter.create_products(product_variants)
