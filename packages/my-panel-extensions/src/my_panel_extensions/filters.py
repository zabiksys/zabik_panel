"""Filtros con sintaxis de criterios de Dynamics NAV.

Convierte una expresión de filtro en un fragmento SQL con bind params de
SQLAlchemy (p.ej. ``:f0``) listo para incrustar en una consulta y ejecutar
con ``sqlalchemy.text()``.

Operadores soportados (estilo Navision):
  valor            Igual
  a..b             Rango cerrado
  ..b / a..        Rango abierto
  a|b              O
  a&b              Y (precedencia mayor que |)
  <>valor          Distinto
  >, >=, <, <=     Comparaciones
  *                Comodín (cualquier número de caracteres)
  ?                Comodín (un carácter)
  @                No distinguir mayúsculas
  ''               Valor en blanco
  'texto'          Literal exacto

El dialecto controla el escapado de LIKE y la semántica de ``@``:
  - mssql: colación case-insensitive, ``@`` es no-op y el escapado usa ``[]``.
  - postgresql: ``LIKE ... ESCAPE '\'``, ``@`` emite ``ILIKE``/``LOWER()``.
"""
from enum import Enum
import re


class Dialect(str, Enum):
    """Dialectos SQL soportados."""
    MSSQL = 'mssql'
    POSTGRESQL = 'postgresql'


class FilterError(ValueError):
    """Error al parsear una expresión de filtro."""


def _norm(value):
    return '' if value is None else str(value).lower()


_LIKE_ESCAPE_MSSQL = {'%': '[%]', '_': '[_]', '[': '[[]', ']': '[]]'}
_LIKE_ESCAPE_POSTGRESQL = {'%': '\\%', '_': '\\_', '\\': '\\\\'}


def _pattern_to_like(pattern, dialect):
    table = (
        _LIKE_ESCAPE_MSSQL
        if dialect is Dialect.MSSQL else _LIKE_ESCAPE_POSTGRESQL)
    out = []
    for ch in pattern:
        if ch == '*':
            out.append('%')
        elif ch == '?':
            out.append('_')
        else:
            out.append(table.get(ch, ch))
    return ''.join(out)


def _pattern_to_regex(pattern):
    out = []
    for ch in pattern:
        if ch == '*':
            out.append('.*')
        elif ch == '?':
            out.append('.')
        else:
            out.append(re.escape(ch))
    return ''.join(out)


class _ParamNamer:
    """Genera nombres únicos de bind params (``f0``, ``f1``, ...)."""

    def __init__(self, prefix='f'):
        self.prefix = prefix
        self.i = 0

    def next(self):
        name = f'{self.prefix}{self.i}'
        self.i += 1
        return name


class FilterNode:
    """Nodo del árbol de filtro."""

    def to_sql(self, column, dialect, namer):
        raise NotImplementedError

    def matches(self, value):
        raise NotImplementedError


class _ComparisonFilter(FilterNode):
    _op = None

    def __init__(self, value, ci=False):
        self.value = value
        self.ci = ci

    def to_sql(self, column, dialect, namer):
        name = namer.next()
        params = {name: self.value}
        if self.ci and dialect is Dialect.POSTGRESQL:
            return f'LOWER({column}) {self._op} LOWER(:{name})', params
        return f'{column} {self._op} :{name}', params

    def matches(self, value):
        return self._compare(_norm(value), _norm(self.value))


class EqualsFilter(_ComparisonFilter):
    _op = '='

    def _compare(self, a, b):
        return a == b


class NotEqualsFilter(_ComparisonFilter):
    _op = '<>'

    def _compare(self, a, b):
        return a != b


class LtFilter(_ComparisonFilter):
    _op = '<'

    def _compare(self, a, b):
        return a < b


class LteFilter(_ComparisonFilter):
    _op = '<='

    def _compare(self, a, b):
        return a <= b


class GtFilter(_ComparisonFilter):
    _op = '>'

    def _compare(self, a, b):
        return a > b


class GteFilter(_ComparisonFilter):
    _op = '>='

    def _compare(self, a, b):
        return a >= b


class _LikeFilter(FilterNode):
    _negate = False

    def __init__(self, pattern, ci=False):
        self.pattern = pattern
        self.ci = ci

    def to_sql(self, column, dialect, namer):
        name = namer.next()
        if self.ci and dialect is Dialect.POSTGRESQL:
            op = 'NOT ILIKE' if self._negate else 'ILIKE'
        else:
            op = 'NOT LIKE' if self._negate else 'LIKE'
        esc = " ESCAPE '\\'" if dialect is Dialect.POSTGRESQL else ''
        value = _pattern_to_like(self.pattern, dialect)
        return f'{column} {op} :{name}{esc}', {name: value}

    def matches(self, value):
        regex = _pattern_to_regex(self.pattern)
        matched = re.fullmatch(regex, value or '', re.IGNORECASE) is not None
        return not matched if self._negate else matched


class LikeFilter(_LikeFilter):
    pass


class NotLikeFilter(_LikeFilter):
    _negate = True


class RangeFilter(FilterNode):
    def __init__(self, start, end, ci=False):
        self.start = start
        self.end = end
        self.ci = ci

    def to_sql(self, column, dialect, namer):
        n0, n1 = namer.next(), namer.next()
        params = {n0: self.start, n1: self.end}
        if self.ci and dialect is Dialect.POSTGRESQL:
            return (f'LOWER({column}) BETWEEN LOWER(:{n0}) '
                    f'AND LOWER(:{n1})', params)
        return f'{column} BETWEEN :{n0} AND :{n1}', params

    def matches(self, value):
        return _norm(self.start) <= _norm(value) <= _norm(self.end)


class BlankFilter(FilterNode):
    def to_sql(self, column, dialect, namer):
        return f"({column} = '' OR {column} IS NULL)", {}

    def matches(self, value):
        return value is None or value == ''


class AndFilter(FilterNode):
    def __init__(self, children):
        self.children = children

    def to_sql(self, column, dialect, namer):
        fragments = []
        params = {}
        for child in self.children:
            fragment, child_params = child.to_sql(column, dialect, namer)
            fragments.append(fragment)
            params.update(child_params)
        return f"({' AND '.join(fragments)})", params

    def matches(self, value):
        return all(child.matches(value) for child in self.children)


class OrFilter(FilterNode):
    def __init__(self, children):
        self.children = children

    def to_sql(self, column, dialect, namer):
        fragments = []
        params = {}
        for child in self.children:
            fragment, child_params = child.to_sql(column, dialect, namer)
            fragments.append(fragment)
            params.update(child_params)
        return f"({' OR '.join(fragments)})", params

    def matches(self, value):
        return any(child.matches(value) for child in self.children)


_CMP_OPS = ('<>', '<=', '>=', '<', '>', '=')


def _split_operator(text, op):
    """Divide por un operador respetando literales entre comillas simples."""
    parts = []
    current = []
    in_quote = False
    for ch in text:
        if ch == "'":
            in_quote = not in_quote
            current.append(ch)
        elif ch == op and not in_quote:
            parts.append(''.join(current))
            current = []
        else:
            current.append(ch)
    parts.append(''.join(current))
    return parts


class _Parser:
    def __init__(self, text):
        self.text = text

    def parse(self):
        or_parts = _split_operator(self.text, '|')
        terms = [self._parse_and(part) for part in or_parts]
        if len(terms) == 1:
            return terms[0]
        return OrFilter(terms)

    def _parse_and(self, text):
        and_parts = _split_operator(text, '&')
        terms = [self._parse_term(part) for part in and_parts]
        if len(terms) == 1:
            return terms[0]
        return AndFilter(terms)

    def _parse_term(self, text):
        text = text.strip()
        if not text:
            raise FilterError('Expresión vacía entre operadores')
        ci = False
        if text.startswith('@'):
            ci = True
            text = text[1:].strip()
        if not text:
            raise FilterError('El operador @ requiere un valor')
        return self._parse_simple(text, ci)

    def _parse_simple(self, text, ci):
        if text.startswith("'"):
            return self._parse_quoted(text, ci)
        for op in _CMP_OPS:
            if text.startswith(op):
                value = text[len(op):].strip()
                if not value:
                    raise FilterError(f'El operador {op} requiere un valor')
                return self._comparison(op, value, ci)
        if '..' in text:
            start, _, end = text.partition('..')
            if '..' in end:
                raise FilterError('Solo se permite un rango (..) por término')
            return self._range(start.strip(), end.strip(), ci)
        return self._value(text, ci)

    def _parse_quoted(self, text, ci):
        if len(text) < 2 or not text.endswith("'"):
            raise FilterError('Comillas simples sin cerrar')
        content = text[1:-1]
        if "'" in content:
            raise FilterError('Comillas mal formadas')
        if content == '':
            return BlankFilter()
        return EqualsFilter(content, ci=ci)

    def _comparison(self, op, value, ci):
        has_wildcard = '*' in value or '?' in value
        if op == '<>':
            if has_wildcard:
                return NotLikeFilter(value, ci=ci)
            return NotEqualsFilter(value, ci=ci)
        if has_wildcard:
            raise FilterError(
                f'El operador {op} no admite comodines (*, ?)')
        if op == '=':
            return EqualsFilter(value, ci=ci)
        by_op = {
            '<': LtFilter, '<=': LteFilter, '>': GtFilter, '>=': GteFilter}
        return by_op[op](value, ci=ci)

    def _range(self, start, end, ci):
        for bound in (start, end):
            if '*' in bound or '?' in bound:
                raise FilterError(
                    'Los extremos del rango no admiten comodines (*, ?)')
        if not start and not end:
            raise FilterError('Rango vacío')
        if start and end:
            return RangeFilter(start, end, ci=ci)
        if end:
            return LteFilter(end, ci=ci)
        return GteFilter(start, ci=ci)

    def _value(self, text, ci):
        if '*' in text or '?' in text:
            return LikeFilter(text, ci=ci)
        return EqualsFilter(text, ci=ci)


def parse_filter(text):
    """Devuelve el árbol de filtro o ``None`` si la expresión está vacía."""
    text = (text or '').strip()
    if not text:
        return None
    return _Parser(text).parse()


def compile_filter(text, column, dialect=Dialect.MSSQL, prefix='f'):
    """Convierte una expresión en (fragmento SQL, dict de params).

    El fragmento usa bind params de SQLAlchemy (``:f0``, ``:f1``, ...). El
    caller debe incrustarlo en la consulta completa y envolverlo con
    ``sqlalchemy.text()``.
    """
    node = parse_filter(text)
    if node is None:
        return '', {}
    namer = _ParamNamer(prefix)
    return node.to_sql(column, dialect, namer)


def filter_matches(text, value):
    """Devuelve si ``value`` cumple la expresión (para reuso en pandas)."""
    node = parse_filter(text)
    if node is None:
        return True
    return node.matches(value)
