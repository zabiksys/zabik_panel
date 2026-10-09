from dataclasses import dataclass
from typing import Annotated

from .title import Title


@dataclass
class Price:
    code: Annotated[str, Title(en='Code', es='Código')]
    price: Annotated[float, Title(en='Price', es='Precio')]