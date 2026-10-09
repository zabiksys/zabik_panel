"""Tests para my_panel_extensions.filters."""
import pytest

from my_panel_extensions.filters import (
    Dialect, FilterError, compile_filter, filter_matches)


MSSQL = Dialect.MSSQL
POSTGRESQL = Dialect.POSTGRESQL
COLUMN = 'sh.No_'


@pytest.mark.parametrize('expr,expected', [
    ('1001', ('sh.No_ = :f0', {'f0': '1001'})),
    ("'1001'", ('sh.No_ = :f0', {'f0': '1001'})),
    ('A%', ('sh.No_ = :f0', {'f0': 'A%'})),
    ('1001..1010',
     ('sh.No_ BETWEEN :f0 AND :f1', {'f0': '1001', 'f1': '1010'})),
    ('..2500', ('sh.No_ <= :f0', {'f0': '2500'})),
    ('23..', ('sh.No_ >= :f0', {'f0': '23'})),
    ('1200|1300',
     ('(sh.No_ = :f0 OR sh.No_ = :f1)',
      {'f0': '1200', 'f1': '1300'})),
    ('<2000&>1000',
     ('(sh.No_ < :f0 AND sh.No_ > :f1)',
      {'f0': '2000', 'f1': '1000'})),
    ('<>0', ('sh.No_ <> :f0', {'f0': '0'})),
    ('<>A*', ('sh.No_ NOT LIKE :f0', {'f0': 'A%'})),
    ('>1200', ('sh.No_ > :f0', {'f0': '1200'})),
    ('<=1200', ('sh.No_ <= :f0', {'f0': '1200'})),
    ('Co*', ('sh.No_ LIKE :f0', {'f0': 'Co%'})),
    ('*Co', ('sh.No_ LIKE :f0', {'f0': '%Co'})),
    ('*Co*', ('sh.No_ LIKE :f0', {'f0': '%Co%'})),
    ('A*B', ('sh.No_ LIKE :f0', {'f0': 'A%B'})),
    ('A* & *B',
     ('(sh.No_ LIKE :f0 AND sh.No_ LIKE :f1)',
      {'f0': 'A%', 'f1': '%B'})),
    ('Hans?n', ('sh.No_ LIKE :f0', {'f0': 'Hans_n'})),
    ('@location', ('sh.No_ = :f0', {'f0': 'location'})),
    ("''", ("(sh.No_ = '' OR sh.No_ IS NULL)", {})),
    ('A*%', ('sh.No_ LIKE :f0', {'f0': 'A%[%]'})),
    ('A_*B', ('sh.No_ LIKE :f0', {'f0': 'A[_]%B'})),
    ('', ('', {})),
    ('A|B&C',
     ('(sh.No_ = :f0 OR (sh.No_ = :f1 AND sh.No_ = :f2))',
      {'f0': 'A', 'f1': 'B', 'f2': 'C'})),
])
def test_mssql(expr, expected):
    assert compile_filter(expr, COLUMN, MSSQL) == expected


@pytest.mark.parametrize('expr,expected', [
    ('1001', ('sh.No_ = :f0', {'f0': '1001'})),
    ('A%', ('sh.No_ = :f0', {'f0': 'A%'})),
    ('1001..1010',
     ('sh.No_ BETWEEN :f0 AND :f1', {'f0': '1001', 'f1': '1010'})),
    ('Co*', ("sh.No_ LIKE :f0 ESCAPE '\\'", {'f0': 'Co%'})),
    ('*Co', ("sh.No_ LIKE :f0 ESCAPE '\\'", {'f0': '%Co'})),
    ('A*B', ("sh.No_ LIKE :f0 ESCAPE '\\'", {'f0': 'A%B'})),
    ('Hans?n', ("sh.No_ LIKE :f0 ESCAPE '\\'", {'f0': 'Hans_n'})),
    ('A*%', ("sh.No_ LIKE :f0 ESCAPE '\\'", {'f0': 'A%\\%'})),
    ('A_*B', ("sh.No_ LIKE :f0 ESCAPE '\\'", {'f0': 'A\\_%B'})),
    ('@location', ('LOWER(sh.No_) = LOWER(:f0)', {'f0': 'location'})),
    ('@A*', ("sh.No_ ILIKE :f0 ESCAPE '\\'", {'f0': 'A%'})),
    ('<>A*', ("sh.No_ NOT LIKE :f0 ESCAPE '\\'", {'f0': 'A%'})),
    ("''", ("(sh.No_ = '' OR sh.No_ IS NULL)", {})),
])
def test_postgresql(expr, expected):
    assert compile_filter(expr, COLUMN, POSTGRESQL) == expected


@pytest.mark.parametrize('expr', [
    'A..B..C',
    'A*..B',
    '..A*',
    '..',
    '>A*',
    "'unclosed",
    "'a''b'",
    'A||B',
    'A&&B',
    '|A',
    'A|',
    'A&',
    '@',
])
def test_invalid(expr):
    with pytest.raises(FilterError):
        compile_filter(expr, COLUMN, MSSQL)


@pytest.mark.parametrize('expr,value,expected', [
    ('1001', '1001', True),
    ('1001', '1002', False),
    ('1001..1010', '1005', True),
    ('1001..1010', '1011', False),
    ('..2500', '2000', True),
    ('..2500', '3000', False),
    ('23..', '30', True),
    ('1200|1300', '1300', True),
    ('<>0', '1', True),
    ('<>0', '0', False),
    ('Co*', 'Company', True),
    ('Co*', 'ACompany', False),
    ('*Co', 'FooCo', True),
    ('*Co', 'Company', False),
    ('*Co*', 'Company', True),
    ('A*B', 'AxxxB', True),
    ('A* & *B', 'AxxxB', True),
    ('A* & *B', 'AxxxC', False),
    ('Hans?n', 'Hansen', True),
    ('Hans?n', 'Hans', False),
    ('@location', 'LOCATION', True),
    ("''", '', True),
    ("''", 'x', False),
    ('', 'anything', True),
])
def test_matches(expr, value, expected):
    assert filter_matches(expr, value) is expected


def test_multiple_prefixes_no_collision():
    order_no_sql, order_no_params = compile_filter(
        'A*', 'sh.No_', MSSQL, prefix='order_no_')
    dept_sql, dept_params = compile_filter(
        'B*', 'sh.Department', MSSQL, prefix='department_')
    order_type_sql, order_type_params = compile_filter(
        'C*', 'order_type.[Dimension Value Code]', MSSQL,
        prefix='order_type_')
    params = {**order_no_params, **dept_params, **order_type_params}
    assert order_no_sql == 'sh.No_ LIKE :order_no_0'
    assert dept_sql == 'sh.Department LIKE :department_0'
    assert order_type_sql == (
        'order_type.[Dimension Value Code] LIKE :order_type_0')
    assert params == {
        'order_no_0': 'A%', 'department_0': 'B%', 'order_type_0': 'C%'}
