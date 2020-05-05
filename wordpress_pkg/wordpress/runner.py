import datetime
import json
import logging
import os
import pathlib
import urllib.parse

import click
from gateway.gateway import Gateway
from wordpress.importers import WoocommerceWordPress

logger = logging.getLogger(__name__)

WOOCOMMERCE_CONSUMER_KEY = os.environ.get("WOOCOMMERCE_CONSUMER_KEY")
WOOCOMMERCE_CONSUMER_SECRET = os.environ.get("WOOCOMMERCE_CONSUMER_SECRET")
WOOCOMMERCE_BASE_URL = os.environ.get("WOOCOMMERCE_BASE_URL")

importer = WoocommerceWordPress(WOOCOMMERCE_CONSUMER_KEY, WOOCOMMERCE_CONSUMER_SECRET, WOOCOMMERCE_BASE_URL, None)

GATEWAY_BASE_URL = os.environ.get("GATEWAY_BASE_URL")
GATEWAY_SHOP_ID = os.environ.get("GATEWAY_SHOP_ID")
GATEWAY_SECRET = os.environ.get("GATEWAY_SECRET")
IMAGE_URL_PREFIX = f"{os.environ.get('IMAGEBUCKET_URL')}{GATEWAY_SHOP_ID}/"


def _map_categories(api_categories, gw_categories) -> dict:
    mapped_categories = dict()
    gw_categories_lower = list(map(str.lower, gw_categories))
    for api_category in map(str.lower, api_categories):
        if api_category in gw_categories_lower:
            mapped_categories[api_category] = api_category
        else:
            mapped_categories[api_category] = None

    return mapped_categories


def _get_category_map(category_map_path: str) -> dict:
    current_directory = pathlib.Path(__file__).parent.absolute()
    try:
        with open(os.path.join(current_directory, category_map_path)) as category_map_file:
            category_map = json.load(category_map_file)
            return category_map
    except FileNotFoundError:
        print(pathlib.Path(__file__).parent.absolute())
        logger.error("File with category map '%s' not found.", category_map_path)
        return None


@click.command()
def prepare_mapping_file():
    current_directory = pathlib.Path(__file__).parent.absolute()
    parsed_url = urllib.parse.urlparse(WOOCOMMERCE_BASE_URL)
    category_mapper_filename = "{domain}_category_map.json".format(domain=parsed_url.netloc)
    exporter = Gateway(GATEWAY_BASE_URL, GATEWAY_SHOP_ID, GATEWAY_SECRET, IMAGE_URL_PREFIX)
    api_categories = importer.get_category_list()
    gw_categories = exporter._get_categories()

    mapped_categories = _map_categories(api_categories, gw_categories)
    with open(category_mapper_filename, "w") as output_file:
        json.dump(mapped_categories, output_file, indent=4)

    print("Generated category map: ", os.path.join(current_directory, category_mapper_filename))


@click.command()
@click.option("--path", "-p", help="Path to mapped categories (json file)")
def sync_categories(category_map_path: str):
    """
    Pass path to a file with mapped categories.
    """
    print("category_map_path")
    category_map = _get_category_map(category_map_path)
    if not category_map:
        return
    importer = WoocommerceWordPress(
        WOOCOMMERCE_CONSUMER_KEY, WOOCOMMERCE_CONSUMER_SECRET, WOOCOMMERCE_BASE_URL, category_map
    )
    exporter = Gateway(GATEWAY_BASE_URL, GATEWAY_SHOP_ID, GATEWAY_SECRET, IMAGE_URL_PREFIX)

    gw_products = exporter.list_of_products()

    for gw_product in gw_products:
        updated_product = importer.sync_categories(gw_product)
        if not updated_product:
            continue

        # TODO method not available
        # exporter.update_product(updated_product)


@click.command()
def run_import(filename):
    print(filename)
    category_map = _get_category_map(filename)
    if not category_map:
        return
    print(WOOCOMMERCE_CONSUMER_KEY)
    importer = WoocommerceWordPress(
        WOOCOMMERCE_CONSUMER_KEY, WOOCOMMERCE_CONSUMER_SECRET, WOOCOMMERCE_BASE_URL, category_map
    )
    exporter = Gateway(GATEWAY_BASE_URL, GATEWAY_SHOP_ID, GATEWAY_SECRET, IMAGE_URL_PREFIX)

    for product_variants in importer.get_products():
        exporter.create_products(product_variants)
