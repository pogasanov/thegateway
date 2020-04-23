import os

import click
from gateway.gateway import Gateway
from wordpress.importers import WoocommerceWordPress


@click.command()
def run_import():
    woocommerce_consumer_key = os.environ.get("WOOCOMMERCE_CONSUMER_KEY", "ck_7311e697cff297153143761909b9127188874571")
    woocommerce_consumer_secret = os.environ.get(
        "WOOCOMMERCE_CONSUMER_SECRET", "cs_26ffecf428f177897fa87afb5b758fd9cb10c8d2"
    )
    woocommerce_base_url = os.environ.get("WOOCOMMERCE_BASE_URL", "http://a41bcc60.ngrok.io")

    gateway_base_url = os.environ.get("GATEWAY_BASE_URL", "https://sma.dev.gwapi.eu")
    gateway_shop_id = os.environ.get("GATEWAY_SHOP_ID", "20c36f95-3bc0-4d66-bb28-9b16ae1146ab")
    gateway_secret = os.environ.get("GATEWAY_SECRET", "feWUIqvODUBvzpISShCxtA9BzAEZ4bAn0CMIfTcFgj8=")
    image_url_prefix = f"{os.environ.get('IMAGEBUCKET_URL')}{gateway_shop_id}/"
    importer = WoocommerceWordPress(woocommerce_consumer_key, woocommerce_consumer_secret, woocommerce_base_url)
    exporter = Gateway(gateway_base_url, gateway_shop_id, gateway_secret, image_url_prefix)
    for product_variants in importer.get_products():
        exporter.create_products(product_variants)
