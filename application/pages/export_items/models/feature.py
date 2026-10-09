from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from typing import Any


class FeatureDataType(Enum):
    INTEGER = 0
    DECIMAL = 1
    TEXT = 2
    DATE = 3
    BOOLEAN = 4
    OPTION = 5


@dataclass
class FeatureAnswer:
    description: str
    line_no_: int


@dataclass
class FeatureQuestion:
    description: str
    line_no_: int
    multiple_answers: bool
    data_type: FeatureDataType
    answers: list[FeatureAnswer]


@dataclass
class Feature:
    title: str
    value: Any


@dataclass
class FeatureQuestions:
    questions: OrderedDict[int, FeatureQuestion]


def uom_state_mapper(x, locale):
    from .unit_of_measure import UOMState
    return {
        UOMState._: {'en': '', 'es': ''},
        UOMState.EXPECTED: {'en': 'Expected', 'es': 'Previsto'},
        UOMState.INVENTED: {'en': 'Invented', 'es': 'Inventado'},
        UOMState.SHIPMARKS: {'en': 'Shipmarks', 'es': 'Shipmarks'},
        UOMState.VERIFIED: {'en': 'Verified', 'es': 'Verificado'}
        }[x][locale]