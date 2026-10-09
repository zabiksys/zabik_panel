from dataclasses import dataclass
from enum import Enum


class UOMState(Enum):
    _ = 0
    INVENTED = 1
    EXPECTED = 2
    VERIFIED = 3
    SHIPMARKS = 4


@dataclass
class UnitOfMeasure:
    code: str
    qty_per_unit_of_measure: float
    height: float
    width: float
    length: float
    cubage: float
    weight: str
    state: UOMState