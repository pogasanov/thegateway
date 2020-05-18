import os

import click
from gateway import Gateway
from selly.importer import SellyImporter

SELLY_API_ID = os.environ.get("SELLY_API_ID")
SELLY_APP_KEY = os.environ.get("SELLY_APP_KEY")
SELLY_SHOP_URL = os.environ.get("SELLY_SHOP_URL")
GATEWAY_BASE_URL = os.environ.get("GATEWAY_BASE_URL", "https://sma.dev.gwapi.eu")
GATEWAY_SHOP_ID = os.environ.get("GATEWAY_SHOP_ID", "a547de18-7a1d-450b-a57b-bbf7f177db84")
GATEWAY_SECRET = os.environ.get("GATEWAY_SECRET", "OyB2YbwTVtRXuJv+VE4oJLVyGo8pf1XVibCk08lt4ys=")

importer = SellyImporter(SELLY_API_ID, SELLY_APP_KEY, SELLY_SHOP_URL)


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    exporter = Gateway(GATEWAY_BASE_URL, GATEWAY_SHOP_ID, GATEWAY_SECRET)
    ctx.obj = {"importer": importer, "exporter": exporter}

    if ctx.invoked_subcommand is None:
        click.echo("Running: run-imports")
        ctx.invoke(run_imports)
    else:
        click.echo(f"Running: {ctx.invoked_subcommand}")


@cli.command()
@click.pass_context
def run_imports(ctx):
    print(SELLY_SHOP_URL)
    importer = ctx.obj["importer"]
    exporter = ctx.obj["exporter"]

    importer.exporter = exporter

    click.echo("Importing products...")
    products = importer.build_products()

    products_count = next(products)
    for index, product in enumerate(products):
        click.echo(f"\rExporting: {index + 1} / {products_count}", nl=False)
        exporter.create_products(product)
