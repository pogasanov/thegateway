import logging

from wordpress.runner import run_import

if __name__ == "__main__":
    logging.basicConfig()
    run_import()
