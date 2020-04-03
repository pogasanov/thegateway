from dataclasses import dataclass, field
from typing import List, Dict

from utils.io import ResponseStream


@dataclass
class Product:
    name: str
    price: float
    stock: float = 0
    description: str = ''
    description_short: str = ''
    sku: str = ''
    images: List[Dict[str, str, ResponseStream]] = field(default_factory=list)
    variant_data: dict = field(default_factory=dict)
