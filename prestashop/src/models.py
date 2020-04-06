from dataclasses import dataclass, field
from typing import List

from utils.io import ResponseStream


@dataclass
class Image:
    filename: str
    mimetype: str
    data: ResponseStream


@dataclass
class Product:
    name: str
    price: float
    vat_percent: int
    stock: float = 0
    description: str = ""
    description_short: str = ""
    sku: str = ""
    images: List[Image] = field(default_factory=list)
    variant_data: dict = field(default_factory=dict)
