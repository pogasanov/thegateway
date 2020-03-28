from prestashop.src.Gateway import Gateway
from prestashop.src.Prestashop import Prestashop


def run_import():
    importer = Prestashop()
    exporter = Gateway()

    products = importer.build_products()
    for product in products:
        exporter.create_product(product)


if __name__ == '__main__':
    run_import()
