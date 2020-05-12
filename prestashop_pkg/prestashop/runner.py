import os

import click
from gateway.gateway import Gateway

from .importers import Prestashop

prestashop_base_url = os.environ.get("PRESTASHOP_BASE_URL", "http://127.0.0.1:8080")
prestashop_api_key = os.environ.get("PRESTASHOP_API_KEY", "RZY9E7L8AP5EPSMDZSXQ2SDJXZCEXBU4")
language_id = os.environ.get("PRESTASHOP_LANGUAGE_ID", None)

gateway_base_url = os.environ.get("GATEWAY_BASE_URL", "https://sma.dev.gwapi.eu")
gateway_shop_id = os.environ.get("GATEWAY_SHOP_ID", "a547de18-7a1d-450b-a57b-bbf7f177db84")
gateway_secret = os.environ.get("GATEWAY_SECRET", "OyB2YbwTVtRXuJv+VE4oJLVyGo8pf1XVibCk08lt4ys=")
image_url_prefix = f"{os.environ.get('IMAGEBUCKET_URL')}{gateway_shop_id}/"

importer = Prestashop(prestashop_base_url, prestashop_api_key, image_url_prefix, language_id=language_id)


@click.command()
def run_import():
    exporter = Gateway(gateway_base_url, gateway_shop_id, gateway_secret, image_url_prefix)
    importer.exporter = exporter

    for product in importer.build_products():
        exporter.create_products(product)
