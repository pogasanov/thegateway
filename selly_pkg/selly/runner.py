import os

from gateway import Gateway
from selly.importer import SellyImporter


def run_imports():
    selly_api_id = os.environ.get("SELLY_API_ID")
    selly_app_key = os.environ.get("SELLY_APP_KEY")
    selly_shop_url = os.environ.get("SELLY_SHOP_URL")
    importer = SellyImporter(selly_api_id, selly_app_key, selly_shop_url)

    gateway_base_url = os.environ.get("GATEWAY_BASE_URL", "https://sma.dev.gwapi.eu")
    gateway_shop_id = os.environ.get("GATEWAY_SHOP_ID", "a547de18-7a1d-450b-a57b-bbf7f177db84")
    gateway_secret = os.environ.get("GATEWAY_SECRET", "OyB2YbwTVtRXuJv+VE4oJLVyGo8pf1XVibCk08lt4ys=")
    image_url_prefix = f"{os.environ.get('IMAGEBUCKET_URL')}{gateway_shop_id}/"
    exporter = Gateway(gateway_base_url, gateway_shop_id, gateway_secret, image_url_prefix)
    print("Importing products...")
    products = importer.build_products()
    products_count = next(products)
    for index, product in enumerate(products):
        print(f"Exporting: {index + 1} / {products_count}")
        exporter.create_products(product)
