from dataclasses import dataclass, field
from typing import List, BinaryIO


@dataclass
class Image:
    filename: str
    mimetype: str
    data: BinaryIO


@dataclass
class Product:
    name: str
    price: float
    stock: float = 0
    description: str = ''
    description_short: str = ''
    sku: str = ''
    images: List[Image] = field(default_factory=list)
    variant_data: dict = field(default_factory=dict)
