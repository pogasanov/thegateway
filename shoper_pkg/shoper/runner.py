import json
import os

from pathlib import Path
from typing import List, Dict

import click
from dotenv import load_dotenv
from gateway.gateway import Gateway
from .importers import Shoper

env_path = Path("../../") / ".env"
load_dotenv(env_path)
GATEWAY_BASE_URL = os.environ.get("GATEWAY_BASE_URL", "https://sma.dev.gwapi.eu")
GATEWAY_SHOP_ID = os.environ.get("GATEWAY_SHOP_ID", "f99424a4-d79b-4e37-aa86-f2ed84c27d7b")
GATEWAY_SECRET = os.environ.get("GATEWAY_SECRET", "/ew7hc6im+sQOHrQK8S0cZ9UXn35lka1SqCrLVRpJKM=")
IMAGE_URL_PREFIX = f"{os.environ.get('IMAGEBUCKET_URL')}{GATEWAY_SHOP_ID}/"
SHOPER_BASE_URL = os.environ.get("SHOPER_BASE_URL", "http://sklep266192.shoparena.pl")
SHOPER_USERNAME = os.environ.get("SHOPER_USERNAME", "karol.ziolkowski@profil-software.com")
SHOPER_PASSWORD = os.environ.get("SHOPER_PASSWORD", "Magik123")


def get_missing_categories(gateway_categories: Dict, importer_categories: List) -> List:
    """
    Return list of categories that do not have their representation
    in gateway categories.
    """
    categories = list()
    for category in importer_categories:
        if not gateway_categories.get(category):
            categories.append(category)
    return categories

@click.command()
def prepare_mapping_file():
    """
    Creates file which maps categories from the ecommerce to the gateway
    categories. Prints out categories from gateway with their ids
    and then prompts user to connect ecommerce category with gateway category
    by passing the id.
    Based on that the file is generated.
    """
    importer = Shoper(SHOPER_BASE_URL, SHOPER_USERNAME, SHOPER_PASSWORD)
    gateway = Gateway(GATEWAY_BASE_URL, GATEWAY_SHOP_ID, GATEWAY_SECRET, IMAGE_URL_PREFIX)
    gateway_categories = gateway._get_categories()
    importer_categories = importer.get_categories_list()
    missing_categories = get_missing_categories(gateway_categories, importer_categories)
    if missing_categories:
        reverted_gateway_categories = dict()
        filename = input("File name:")
        for name, _id in gateway_categories:
            print(f"{_id}: {name}")
            reverted_gateway_categories.update({_id: name})
        print("Pass id of a category to be mapped: \n")
        categories = dict()
        for category in missing_categories:
            _id = input(f"{category}: ")
            categories.update({category: reverted_gateway_categories.get(_id)})
        with open(f"{filename}.txt") as file:
            file.write(json.dumps(categories))
    else:
        print("All categories are covered with categories from the gateway.")


@click.command()
@click.option("--path", "-p")
def sync_categories(path):
    """
    Pass path to a file with mapped categories.
    """
    with open(path) as file:
        importer = Shoper(SHOPER_BASE_URL, SHOPER_USERNAME, SHOPER_PASSWORD)
        gateway = Gateway(GATEWAY_BASE_URL, GATEWAY_SHOP_ID, GATEWAY_SECRET, IMAGE_URL_PREFIX)
        products = gateway.list_of_products()
        importer_categories = importer._get_categories()
        categories = json.loads(file)
        for grouped_product in products:
            for product in grouped_product:
                importer_product = importer.fetch_product(product)
                category = importer_categories.get(importer_product.get("category_id"))
                mapped_category = categories.get(category)
                if mapped_category:
                    product.category = [mapped_category]
                # if mapped category is None then the category is covered by gateway categories
                # or there was no matching category
                else:
                    product.category = [category]
                # TODO gateway.update(product)


@click.command
def run_import():
    importer = Shoper(SHOPER_BASE_URL, SHOPER_USERNAME, SHOPER_PASSWORD)
    gateway = Gateway(GATEWAY_BASE_URL, GATEWAY_SHOP_ID, GATEWAY_SECRET, IMAGE_URL_PREFIX)

    for product_list in importer.fetch_products():
        gateway.create_products(product_list)
