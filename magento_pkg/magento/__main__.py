import logging

from magento.runner import run_import

# pylint: disable=E1120
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_import()
