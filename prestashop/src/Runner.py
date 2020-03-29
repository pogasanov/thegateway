import os

from exporters import Gateway
from importers import Prestashop


def run_import():
    PRESTASHOP_BASE_URL = os.environ.get('PRESTASHOP_BASE_URL', 'http://127.0.0.1:8080')
    PRESTASHOP_API_KEY = os.environ.get('PRESTASHOP_API_KEY', 'RZY9E7L8AP5EPSMDZSXQ2SDJXZCEXBU4')
    importer = Prestashop(PRESTASHOP_BASE_URL, PRESTASHOP_API_KEY)

    GATEWAY_BASE_URL = os.environ.get('GATEWAY_BASE_URL', 'https://sma.dev.gwapi.eu')
    GATEWAY_SHOP_ID = os.environ.get('GATEWAY_SHOP_ID', 'a547de18-7a1d-450b-a57b-bbf7f177db84')
    GATEWAY_SECRET = os.environ.get('GATEWAY_SECRET', 'OyB2YbwTVtRXuJv+VE4oJLVyGo8pf1XVibCk08lt4ys=')
    exporter = Gateway(GATEWAY_BASE_URL, GATEWAY_SHOP_ID, GATEWAY_SECRET)

    products = importer.build_products()
    for product in products:
        exporter.create_product(product)


if __name__ == '__main__':
    run_import()
