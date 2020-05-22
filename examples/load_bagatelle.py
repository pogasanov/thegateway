import logging
import re
import uuid
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal

import click
import xlrd
from gwio.environment import Env

from gwio.ext.vat import VatPrice
from gwio.models.pricing import PriceType
from gwio.models.products._vertical.sma.product import Product as BaseProduct
from gwio.models.tags import (
    ProductTags as ProductTag,
    TagType,
    Tags as Tag,
)
from gwio.models.webshops import (
    Webshop,
    WebshopProduct,
)

logger = logging.getLogger(__name__)

NCS_RE = re.compile(r'^(?P<name>[^.]+)\.(?P<color>[^/]+)/(?P<size>.*)')
NC_RE = re.compile(r'^(?P<name>[^.]+)\.(?P<color>.+)')
NS_RE = re.compile(r'^(?P<name>[^.]+)/(?P<size>.+)')


@dataclass
class BagatelleProduct:
    name: str
    sku: int
    base_price: VatPrice
    color: str = ''
    size: str = ''
    stock_level: int = 0
    namespace = None

    @property
    def guid(self):
        return self._guid(self.sku)

    @classmethod
    def _guid(cls, sku):
        guid = uuid.uuid5(cls.namespace, str(sku))
        return guid

    def as_base_product(self, owner=None):
        variants = dict()
        if self.size:
            variants['size'] = self.size
        if self.color:
            variants['color'] = self.color
        return BaseProduct(
            guid=self.guid,
            name=self.name,
            data=dict(variants=variants, sku=self.sku),
            base_price=self.base_price,
            base_price_type=PriceType.RETAIL,
            cost_price=VatPrice(0, vat=0),
            owner_guid=owner
        )

class Processor:
    def __init__(self, shop):
        self.shop = shop

    def create(self, products, variants):
        if not click.confirm(f"Are you sure you want to import {len(variants)} products and {len(products)} variants to {Env.NAMESPACE}"):
            return
        logger.info("Importing")

        self.create_variants(variants)
        self.create_products(products, variants)


    def create_products(self, products, variants):
        try:
            with open(f"{self.shop.name}.state") as f:
                self.seen_products = set(l.strip() for l in f)
        except OSError:
            self.seen_products = set()
        if not click.confirm(f"Are you sure you want to create {len(products)} variant products in {Env.NAMESPACE}"):
            return
        with open(f"{self.shop.name}.state", 'a+') as f:
            for product in products:
                if product.sku in self.seen_products:
                    logger.info(f"Skipping {product.sku} as seen")
                    continue
                else:
                    f.write(f'{product.sku}\n')
                logger.info(f'{product.name} {product.sku} {product.guid}')
                base_product = product.as_base_product(self.shop.guid)
                logger.info(base_product)
                base_product.save()
                if product.name in variants:
                    pt = ProductTag(tag_guid=BagatelleProduct._guid(product.name), product_guid=product.guid)
                    logger.info(pt)
                    pt.save()

                sp = WebshopProduct(
                    webshop_guid=self.shop.guid,
                    product_guid=product.guid,
                    stock_level=product.stock_level,
                    for_sale=product.stock_level > 0
                )
                sp.save()


    def create_variants(self, variants):
        if not click.confirm(f"Are you sure you want to create {len(variants)} variant tags in {Env.NAMESPACE}"):
            return
        for variant in variants.keys():
            if not variant:
                continue
            tag = Tag(
                owner=self.shop.guid,
                name=variant,
                guid=BagatelleProduct._guid(variant),
                type=TagType.VARIANT
            )
            logger.info(tag)
            tag.save()


def get_webshop(name):
    for ws in Webshop.scan(filter_condition=Webshop.name == name):
        return ws
    else:
        raise LookupError


def main():
    ws = get_webshop("Bagatelle")
    BagatelleProduct.namespace = ws.guid
    processor = Processor(ws)
    logger.info("Loading data.")
    with xlrd.open_workbook('tabela.xlsx') as wb:
        logger.info(wb.sheet_names())
        product_data = wb.sheet_by_index(0)
        rows = product_data.get_rows()
        headers = next(rows)
        variants = defaultdict(list)
        products = list()
        for rowno, row in enumerate(rows):
            if len(row) != 14:
                logger.fatal(f"Malformed row {row}")
            logger.info(row)
            try:
                sku = row[0].value
            except ValueError:
                logger.fatal(f'{sku} is invalid SKU')
                continue
            data = row[2].value
            product_dict = match_data(data)
            product_dict['sku'] = sku
            vat_text = row[9].value
            if vat_text != 'VAT23':
                logger.fatal("Invalid VAT info")
                continue
            stock_level = Decimal(row[7].value) if row[7].value else 0
            product = BagatelleProduct(
                **product_dict,
                base_price=VatPrice(value=Decimal(row[5].value), vat=23),
                stock_level=stock_level
            )
            variants[product.name].append(sku)
            products.append(product)
    logger.info("Loaded")
    processor.create(products, variants)


def match_data(data):
    for regex in (NCS_RE, NC_RE, NS_RE):
        m = regex.match(data)
        if m:
            return m.groupdict()
    logger.error(f"Can't parse name.color/size from {data}")
    return dict(name=data)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
