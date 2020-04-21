from dataclasses import dataclass, field
from decimal import Decimal
from typing import List

from gateway.io import ResponseStream

DEFAULT_VAT_RATE_IN_POLAND = 23


@dataclass
class Image:
    filename: str
    mimetype: str
    data: ResponseStream


# pylint: disable=too-many-instance-attributes
@dataclass
class Product:
    """
    If product has public images then images_urls should be set to list of urls to them.
    If product doesn't have public images then images should be set to list of Image objects.
    """

    name: str
    price: Decimal
    vat_percent: int = DEFAULT_VAT_RATE_IN_POLAND
    stock: Decimal = 0
    description: str = ""
    description_short: str = ""
    sku: str = ""
    images: List[Image] = field(default_factory=list)
    images_urls: List[str] = field(default_factory=list)
    variant_data: dict = field(default_factory=dict)
    for_sale: bool = True
