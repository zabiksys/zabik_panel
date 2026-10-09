from dataclasses import dataclass
from typing import Callable


@dataclass
class Origin:
    process: Callable[[Session, Row], Any]
    formatter: dict | None = None
    column_list: list[str] = field(default_factory=list)

