from dataclasses import dataclass, field
from typing import List


@dataclass
class Product:
    name: str
    price: float
    stock: float = 0
    description: str = ''
    description_short: str = ''
    sku: str = ''
    images: List[object] = field(default_factory=list)
    variant_data: dict = field(default_factory=dict)
