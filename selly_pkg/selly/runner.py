import json
import os
import pathlib

import click

from gateway import Gateway
from selly.importer import SellyImporter

SELLY_API_ID = os.environ.get("SELLY_API_ID")
SELLY_APP_KEY = os.environ.get("SELLY_APP_KEY")
SELLY_SHOP_URL = os.environ.get("SELLY_SHOP_URL")
GATEWAY_BASE_URL = os.environ.get("GATEWAY_BASE_URL", "https://sma.dev.gwapi.eu")
GATEWAY_SHOP_ID = os.environ.get("GATEWAY_SHOP_ID", "a547de18-7a1d-450b-a57b-bbf7f177db84")
GATEWAY_SECRET = os.environ.get("GATEWAY_SECRET", "OyB2YbwTVtRXuJv+VE4oJLVyGo8pf1XVibCk08lt4ys=")
IMAGE_URL_PREFIX = f"{os.environ.get('IMAGEBUCKET_URL')}{GATEWAY_SHOP_ID}/"


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    importer = SellyImporter(SELLY_API_ID, SELLY_APP_KEY, SELLY_SHOP_URL)
    exporter = Gateway(GATEWAY_BASE_URL, GATEWAY_SHOP_ID, GATEWAY_SECRET, IMAGE_URL_PREFIX)
    ctx.obj = {"importer": importer, "exporter": exporter}

    if ctx.invoked_subcommand is None:
        click.echo("Running: run-imports")
        ctx.invoke(run_imports)
    else:
        click.echo(f"Running: {ctx.invoked_subcommand}")


@cli.command()
@click.option("--name", prompt="Retailer name", help="Name of the retailer for which categories will be mapped")
@click.pass_context
def map_categories(ctx, name):
    importer = ctx.obj["importer"]
    exporter = ctx.obj["exporter"]

    importer_categories = importer.get_categories()
    exporter_categories = exporter._get_categories()

    not_mapped_categories = filter(lambda category: category not in exporter_categories, importer_categories)
    output_dict = {category: None for category in not_mapped_categories}
    click.echo(f"{len(output_dict)} / {len(importer_categories)} could not be mapped")
    if output_dict:
        parent_path = pathlib.Path(__file__).parent.parent.absolute()
        file_name = f"{name}-categories-mapping.json"
        file_path = os.path.join(parent_path, "category_mappings", file_name)
        with open(file_path, "w") as outfile:
            json.dump(output_dict, outfile, ensure_ascii=False, indent=4)
        click.echo(f"Generated category map file: {file_path}")
    else:
        click.echo("All categories are covered with categories from the gateway.")


@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.pass_context
def run_imports(ctx, filepath):
    importer = ctx.obj["importer"]
    exporter = ctx.obj["exporter"]

    category_mapping = None
    if filepath:
        with open(filepath, "r") as fin:
            category_mapping = json.load(fin)
        click.echo("Category mapping file loaded")

    click.echo("Importing products...")
    products = importer.build_products(category_mapping)
    products_count = next(products)
    for index, product in enumerate(products):
        click.echo(f"Exporting: {index + 1} / {products_count}")
        exporter.create_products(product)
