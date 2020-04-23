import os

from pathlib import Path

from dotenv import load_dotenv
from gateway.gateway import Gateway
from .importers import Shoper


def run_import():
    env_path = Path("../../") / ".env"
    load_dotenv(env_path)

    shoper_base_url = os.environ.get("SHOPER_BASE_URL", "http://sklep266192.shoparena.pl")
    shoper_username = os.environ.get("SHOPER_USERNAME", "karol.ziolkowski@profil-software.com")
    shoper_password = os.environ.get("SHOPER_PASSWORD", "Magik123")

    gateway_base_url = os.environ.get("GATEWAY_BASE_URL", "https://sma.dev.gwapi.eu")
    gateway_shop_id = os.environ.get("GATEWAY_SHOP_ID", "f99424a4-d79b-4e37-aa86-f2ed84c27d7b")
    gateway_secret = os.environ.get("GATEWAY_SECRET", "/ew7hc6im+sQOHrQK8S0cZ9UXn35lka1SqCrLVRpJKM=")
    image_url_prefix = f"{os.environ.get('IMAGEBUCKET_URL')}{gateway_shop_id}/"
    importer = Shoper(shoper_base_url, shoper_username, shoper_password)
    exporter = Gateway(gateway_base_url, gateway_shop_id, gateway_secret, image_url_prefix)

    for product_list in importer.fetch_products():
        exporter.create_products(product_list)
