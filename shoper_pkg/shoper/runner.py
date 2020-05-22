import os

from pathlib import Path

import click
from dotenv import load_dotenv
from gateway.gateway import Gateway
from shoper.importers import Shoper

env_path = Path("../../") / ".env"
load_dotenv(env_path)
GATEWAY_BASE_URL = os.environ.get("GATEWAY_BASE_URL", "https://sma.dev.gwapi.eu")
GATEWAY_SHOP_ID = os.environ.get("GATEWAY_SHOP_ID", "f99424a4-d79b-4e37-aa86-f2ed84c27d7b")
GATEWAY_SECRET = os.environ.get("GATEWAY_SECRET", "/ew7hc6im+sQOHrQK8S0cZ9UXn35lka1SqCrLVRpJKM=")
SHOPER_BASE_URL = os.environ.get("SHOPER_BASE_URL", "http://sklep266192.shoparena.pl")
SHOPER_USERNAME = os.environ.get("SHOPER_USERNAME", "karol.ziolkowski@profil-software.com")
SHOPER_PASSWORD = os.environ.get("SHOPER_PASSWORD", "Magik123")
gateway = Gateway(GATEWAY_BASE_URL, GATEWAY_SHOP_ID, GATEWAY_SECRET)
importer = Shoper(
    SHOPER_BASE_URL,
    SHOPER_USERNAME,
    SHOPER_PASSWORD,
    exporter=gateway,
    stock_update=False,
)


@click.command
def run_import():
    print(SHOPER_BASE_URL)
    for product_list in importer.fetch_products():
        gateway.create_products(product_list)
