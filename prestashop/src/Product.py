from dataclasses import dataclass


@dataclass
class Product:
    name: str
    price: float
    stock: float = 0
    description: str = ''
    description_short: str = ''
    sku: str = ''
