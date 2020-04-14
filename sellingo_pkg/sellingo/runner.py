import os
import sys

from gateway.gateway import Gateway

from .importer import Sellingo


def run_imports():
    sellingo_shop_url = os.environ.get("SELLINGO_SHOP_URL", "https://demo.sellingo.pl/")
    sellingo_filepath = os.environ.get("SELLINGO_EXPORT_FILE_PATH")
    if not sellingo_filepath:
        print("You have to set SELLINGO_EXPORT_FILE_PATH environmental variable")
        sys.exit(1)
    runner = Sellingo(filepath=sellingo_filepath, shop_url=sellingo_shop_url)

    gateway_base_url = os.environ.get("GATEWAY_BASE_URL", "https://sma.dev.gwapi.eu")
    gateway_shop_id = os.environ.get("GATEWAY_SHOP_ID", "a547de18-7a1d-450b-a57b-bbf7f177db84")
    gateway_secret = os.environ.get("GATEWAY_SECRET", "OyB2YbwTVtRXuJv+VE4oJLVyGo8pf1XVibCk08lt4ys=")
    image_url_prefix = f"{os.environ.get('IMAGEBUCKET_URL')}{gateway_shop_id}/"
    exporter = Gateway(gateway_base_url, gateway_shop_id, gateway_secret, image_url_prefix)

    products = runner.build_products()
    products_count = len(products)
    for index, product in enumerate(products):
        print(f"Exporting: {index + 1} / {products_count}")
        exporter.create_products(product)
