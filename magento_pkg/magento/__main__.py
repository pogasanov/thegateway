import logging

from magento_pkg.magento.runner import run_import

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_import()
