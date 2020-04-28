import os

from gateway.gateway import Gateway

from .importer import Sellingo


def run_imports():
    sellingo_api_url = os.environ.get("SELLINGO_API_URL")
    sellingo_api_key = os.environ.get("SELLINGO_API_KEY")
    importer = Sellingo(api_url=sellingo_api_url, api_key=sellingo_api_key)

    gateway_base_url = os.environ.get("GATEWAY_BASE_URL", "https://sma.dev.gwapi.eu")
    gateway_shop_id = os.environ.get("GATEWAY_SHOP_ID", "a547de18-7a1d-450b-a57b-bbf7f177db84")
    gateway_secret = os.environ.get("GATEWAY_SECRET", "OyB2YbwTVtRXuJv+VE4oJLVyGo8pf1XVibCk08lt4ys=")
    image_url_prefix = f"{os.environ.get('IMAGEBUCKET_URL')}{gateway_shop_id}/"
    exporter = Gateway(gateway_base_url, gateway_shop_id, gateway_secret, image_url_prefix)

    products = importer.build_products()
    products_count = next(products)
    for index, product in enumerate(products):
        print(f"Exporting: {index + 1} / {products_count}")
        exporter.create_products(product)
