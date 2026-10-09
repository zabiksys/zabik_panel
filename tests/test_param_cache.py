"""Test param cache."""
from shutil import rmtree
import sys
from tempfile import mkdtemp
import types

from my_panel_extensions.param_cache import ParamCache
from my_panel_extensions.param_cache import ParamCache2
import pytest


@pytest.fixture
def param_cache():
    temp_dir = mkdtemp()
    yield ParamCache(temp_dir)
    rmtree(temp_dir)


@pytest.fixture
def param_cache2():
    temp_dir = mkdtemp()
    yield ParamCache2(temp_dir)
    rmtree(temp_dir)


class TestParamCache:

    def test_set_get(self, param_cache2):
        param_cache2.set(['i1'], 32)
        param_cache2.set(['i2'], 2)
        assert param_cache2.get(['i1']) == 32
        assert param_cache2.get(['i2']) == 2

    def test_get_keyerror(self, param_cache2):
        with pytest.raises(KeyError):
            param_cache2.get(['i1'])

    def test_hierarchy(self, param_cache2):
        param_cache2.set(['i1', 'i2', 'i3'], 'this is a text 1')
        param_cache2.set(['i1', 'i2', 'i4'], 'this is a text 2')
        param_cache2.set(['i1', 'i4', 'i3'], 'this is a text 3')
        param_cache2.set(['i4', 'i2', 'i3'], 'this is a text 4')
        assert param_cache2.get(['i1', 'i2', 'i3']) == 'this is a text 1'
        assert param_cache2.get(['i1', 'i2', 'i4']) == 'this is a text 2'
        assert param_cache2.get(['i1', 'i4', 'i3']) == 'this is a text 3'
        assert param_cache2.get(['i4', 'i2', 'i3']) == 'this is a text 4'
        assert param_cache2.get(['i4']) == {'i2': {'i3': 'this is a text 4'}}

    def test_hierarchy_keyerror(self, param_cache2):
        param_cache2.set(['i1', 'i2', 'i3'], 'this is a text')
        with pytest.raises(KeyError):
            param_cache2.get(['i1', 'i2', 'i4'])
            param_cache2.get(['i1', 'i4'])
            param_cache2.get(['i4'])
            param_cache2.get(['i1', 'i2', 'i4', 'i5'])

    def test_clear(self, param_cache2):
        param_cache2.set(['i1'], 32)
        param_cache2.clear(['i1'])
        with pytest.raises(KeyError):
            param_cache2.get(['i1'])

    def test_clear_hierarchy(self, param_cache2):
        param_cache2.set(['i1', 'i2', 'i3'], 32)
        param_cache2.set(['i1', 'i5', 'i6'], 2)
        param_cache2.clear(['i1', 'i2'])
        with pytest.raises(KeyError):
            param_cache2.get(['i1', 'i2', 'i3'])
            param_cache2.get(['i1', 'i2'])

        assert param_cache2.get(['i1', 'i5', 'i6']) == 2

    def test_exists(self, param_cache2):
        param_cache2.set(['i1', 'i2', 'i3'], 32)
        assert param_cache2.exists(['i1', 'i2', 'i3'])
        assert param_cache2.exists(['i1', 'i2'])
        assert param_cache2.exists(['i1'])
        assert not param_cache2.exists(['i1', 'i2', 'i4'])
        assert not param_cache2.exists(['i1', 'i4', 'i3'])
        assert not param_cache2.exists(['i4', 'i2', 'i3'])
        assert not param_cache2.exists(['i1', 'i4'])
        assert not param_cache2.exists(['i4'])

    def test_dump_to_dict(self, param_cache2):
        param_cache2.set(['i1', 'i2', 'i3'], 32)
        param_cache2.set(['i1', 'i5', 'i6'], 2)
        assert param_cache2.dump_to_dict() == {
            'i1': {'i2': {'i3': 32}, 'i5': {'i6': 2}}}

    def test_dump_to_dict_unreadable_entry(self, param_cache2):
        param_cache2.set(['i1', 'i2', 'i3'], 32)
        _store_unreadable_entry(param_cache2, 'i2')
        assert param_cache2.dump_to_dict() == {
            'i1': {'i2': {'i3': 32}}}
        assert not param_cache2.exists(['i2'])

    def test_set_with_unreadable_entry(self, param_cache2):
        _store_unreadable_entry(param_cache2, 'i2')
        param_cache2.set(['i2', 'i3', 'i4'], 'value')
        assert param_cache2.get(['i2', 'i3', 'i4']) == 'value'

    def test_clear_with_unreadable_entry(self, param_cache2):
        _store_unreadable_entry(param_cache2, 'i2')
        param_cache2.clear(['i2', 'i3'])
        assert not param_cache2.exists(['i2'])
        with pytest.raises(KeyError):
            param_cache2.get(['i2'])

    def test_load_from_dict(self, param_cache2):
        param_cache2.set(['i7', 'i2', 'i3'], 32)
        param_cache2.set(['i7', 'i5', 'i6'], 2)
        param_cache2.load_from_dict(
            {'i1': {'i2': {'i3': 67}, 'i5': {'i6': 4}}})
        assert param_cache2.get(['i1', 'i2', 'i3']) == 67
        assert param_cache2.get(['i1', 'i5', 'i6']) == 4
        assert not param_cache2.exists(['i7', 'i2', 'i3'])
        assert not param_cache2.exists(['i7', 'i5', 'i6'])

    def test_migrate(self, param_cache, param_cache2):
        param_cache.set('i1.i2.i3', 'this is a text 1')
        param_cache.set('i1.i2.i4', 'this is a text 2')
        param_cache.set('i5.i6.i7', 'this is a text 3')
        param_cache2.migrate(param_cache)
        assert param_cache2.get(['i1', 'i2', 'i3']) == 'this is a text 1'
        assert param_cache2.get(['i1', 'i2', 'i4']) == 'this is a text 2'
        assert param_cache2.get(['i5', 'i6', 'i7']) == 'this is a text 3'


def _store_unreadable_entry(param_cache2: ParamCache2, key: str) -> None:
    """Stores a value that cannot be unpickled once the served app module
    (bokeh_app_*) is gone after a restart."""
    module_name = f'bokeh_app_{key}'
    module = types.ModuleType(module_name)
    klass = type('App', (), {})
    klass.__module__ = module_name
    module.App = klass
    sys.modules[module_name] = module
    try:
        param_cache2.index[key] = klass()
    finally:
        del sys.modules[module_name]
