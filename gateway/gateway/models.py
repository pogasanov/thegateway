from dataclasses import dataclass, field
from decimal import Decimal
from typing import List

from gateway.io import ResponseStream


@dataclass
class Image:
    filename: str
    mimetype: str
    data: ResponseStream


@dataclass
class Product:
    name: str
    price: Decimal
    vat_percent: int
    stock: Decimal = 0
    description: str = ""
    description_short: str = ""
    sku: str = ""
    images: List[Image] = field(default_factory=list)
    variant_data: dict = field(default_factory=dict)
