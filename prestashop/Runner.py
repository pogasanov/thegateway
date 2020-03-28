from prestashop.src.Gateway import Gateway
from prestashop.src.PrestashopImporter import PrestashopImporter


def run_import():
    importer = PrestashopImporter()
    exporter = Gateway()

    products = importer.build_products()
    for product in products:
        exporter.create_product(product)


if __name__ == '__main__':
    run_import()
