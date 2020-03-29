from dataclasses import dataclass, field
from tempfile import SpooledTemporaryFile
from typing import List


@dataclass
class Product:
    name: str
    price: float
    stock: float = 0
    description: str = ''
    description_short: str = ''
    sku: str = ''
    images: List[SpooledTemporaryFile] = field(default_factory=list)
