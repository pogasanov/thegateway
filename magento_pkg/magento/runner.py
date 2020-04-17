import os

import click
from gateway import Gateway

from .importers import Magento


@click.command()
@click.argument("action", type=click.Choice(["import", "sync"], case_sensitive=False), default="import")
def run_import(action):
    magento_base_url = os.environ.get("MAGENTO_BASE_URL", "http://127.0.0.1")
    magento_access_token = os.environ.get("MAGENTO_API_ACCESS_TOKEN", "lrz7qqi7c3yp4rpfhxzn69dz9dyxwz3k")

    gateway_base_url = os.environ.get("GATEWAY_BASE_URL", "https://sma.dev.gwapi.eu")
    gateway_shop_id = os.environ.get("GATEWAY_SHOP_ID", "a547de18-7a1d-450b-a57b-bbf7f177db84")
    gateway_secret = os.environ.get("GATEWAY_SECRET", "OyB2YbwTVtRXuJv+VE4oJLVyGo8pf1XVibCk08lt4ys=")
    image_url_prefix = f"{os.environ.get('IMAGEBUCKET_URL')}{gateway_shop_id}/"

    importer = Magento(magento_base_url, magento_access_token)
    exporter = Gateway(gateway_base_url, gateway_shop_id, gateway_secret, image_url_prefix)

    if action == "import":
        for product in importer.build_products():
            exporter.create_products(product)
    elif action == "sync":
        for product in exporter.list_of_products():
            importer.sync_products(product)
