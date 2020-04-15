import os

import click
from gateway.gateway import Gateway

from .importers import IdoSell


@click.command()
def run_import():
    idosell_login = os.environ.get("IDOSELL_LOGIN")
    idosell_password = os.environ.get("IDOSELL_PASSWORD")
    idosell_base_url = os.environ.get("IDOSELL_BASE_URL")

    gateway_base_url = os.environ.get("GATEWAY_BASE_URL", "https://sma.dev.gwapi.eu")
    gateway_shop_id = os.environ.get("GATEWAY_SHOP_ID", "20c36f95-3bc0-4d66-bb28-9b16ae1146ab")
    gateway_secret = os.environ.get("GATEWAY_SECRET", "feWUIqvODUBvzpISShCxtA9BzAEZ4bAn0CMIfTcFgj8=")
    image_url_prefix = f"{os.environ.get('IMAGEBUCKET_URL')}{gateway_shop_id}/"
    importer = IdoSell(idosell_login, idosell_password, idosell_base_url)
    exporter = Gateway(gateway_base_url, gateway_shop_id, gateway_secret, image_url_prefix)

    for product_variants in importer.get_products():
        exporter.create_products(product_variants)