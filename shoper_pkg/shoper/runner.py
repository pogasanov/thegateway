import json
import os

from pathlib import Path

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


@click.command()
def prepare_mapping_file():
    importer = Shoper(SHOPER_BASE_URL, SHOPER_USERNAME, SHOPER_PASSWORD)
    gateway = Gateway(GATEWAY_BASE_URL, GATEWAY_SHOP_ID, GATEWAY_SECRET, IMAGE_URL_PREFIX)
    gateway_categories = gateway._get_categories()
    importer_categories = importer.get_categories_list()
    reverted_gateway_categories = dict()
    filename = input("File name:")
    for name, _id in gateway_categories:
        print(f"{_id}: {name}")
        reverted_gateway_categories.update({_id: name})
    print("Pass id of a category to be mapped: \n")
    categories = dict()
    for category in importer_categories:
        _id = input(f"{category}: ")
        categories.update({category: reverted_gateway_categories.get(_id)})
    with open(f"{filename}.txt") as file:
        file.write(json.dumps(categories))


@click.command()
@click.option("--path", "-p")
def sync_categories(path):
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
                product.category = [mapped_category]
                # TODO gateway.update(product)


@click.command
def run_import():
    importer = Shoper(SHOPER_BASE_URL, SHOPER_USERNAME, SHOPER_PASSWORD)
    gateway = Gateway(GATEWAY_BASE_URL, GATEWAY_SHOP_ID, GATEWAY_SECRET, IMAGE_URL_PREFIX)

    for product_list in importer.fetch_products():
        gateway.create_products(product_list)
