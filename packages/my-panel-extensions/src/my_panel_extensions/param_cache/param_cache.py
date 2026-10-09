"""param cache."""
from copy import deepcopy
import logging
from pathlib import Path
from typing import Any, Callable

from diskcache import Index, JSONDisk


logger = logging.getLogger(__name__)


class NullMarker:
    pass


class MissingValue:
    pass


NullMarker = NullMarker()
MissingValue = MissingValue()


def get_param_cache(directory: Path) -> Callable:
    index = Index(str(directory), disk=JSONDisk)

    def get_param(
            key: list[str],
            values: list[Any],
            default: Any | None = NullMarker) -> Any:
        cache = index
        if default == NullMarker:
            default = values[0]

        for k in key:
            if k in cache:
                cache = cache[k]
            elif k == key[-1]:
                cache[k] = default
            else:
                cache[k] = {}
                cache = cache[k]

        if cache not in values:
            cache = default
        return cache

    return get_param


class ParamCache():

    def __init__(self, directory: Path):
        self.index = Index(str(directory), disk=JSONDisk)

    def get(
            self,
            key: str,
            values: list[Any] | None = None,
            default: Any | None = NullMarker) -> Any:
        default_value = deepcopy(default)
        if default_value == NullMarker:
            if values:
                default_value = values[0]
            else:
                default_value = None

        if key not in self.index:
            self.index[key] = default
        result = self.index[key]

        # check if saved val is still valid
        if values:
            if type(result) is list:
                new_result = [r for r in result if r in values]
                if result != new_result and new_result:
                    self.index[key] = new_result
            elif result not in values:
                self.index[key] = default_value

        return self.index[key]

    def set(self, key: list[str] | str, value: Any | None) -> None:
        self.index[key] = value

    def clear(self, key: str) -> None:
        if key in self.index:
            del self.index[key]


class ParamCache2:

    def __init__(self, directory: Path):
        self.index = Index(str(directory), disk=JSONDisk)

    def get(
            self,
            key: list[str],
            default: Any | None = MissingValue) -> Any:
        store = self.index
        keys = []
        for k in key:
            keys.append(k)
            try:
                param = store.get(k, MissingValue)
            except ModuleNotFoundError:
                param = MissingValue
            if param is MissingValue:
                if default is MissingValue:
                    raise KeyError(f'Key {keys} not found.')
                else:
                    return default
            else:
                store = param
        return store

    def set(self, key: list[str], value: Any) -> None:
        if len(key) == 1:
            value_to_store = value
        else:
            try:
                leaf = self.index.get(key[0], {})
            except Exception as e:
                logger.warning(
                    'Discarding unreadable cache entry %r: %s', key[0], e)
                try:
                    del self.index[key[0]]
                except Exception:
                    pass
                leaf = {}
            value_to_store = leaf
            if len(key) > 2:
                for k in key[1:-1]:
                    if k not in leaf:
                        leaf[k] = {}
                    leaf = leaf[k]
            leaf[key[-1]] = value

        self.index[key[0]] = value_to_store

    def clear(self, key: list[str]) -> None:
        if len(key) == 1:
            del self.index[key[0]]
        else:
            try:
                value = self.index.get(key[0], MissingValue)
            except Exception as e:
                logger.warning(
                    'Discarding unreadable cache entry %r: %s', key[0], e)
                try:
                    del self.index[key[0]]
                except Exception:
                    pass
                return
            if value is not MissingValue:
                leaf = value
                for k in key[1:-1]:
                    leaf = leaf.get(k, MissingValue)
                    if leaf is MissingValue:
                        return
                del leaf[key[-1]]
                self.index[key[0]] = value

    def exists(self, key: list[str]) -> bool:
        try:
            if key[0] not in self.index:
                return False
        except ModuleNotFoundError:
            return False
        value = deepcopy(self.index[key[0]])
        for k in key[1:]:
            if k not in value:
                return False
            value = value[k]
        return True

    def dump_to_dict(self) -> dict:
        d = {}
        for k in self.index:
            if k != 'disk':
                try:
                    d[k] = self.index[k]
                except Exception as e:
                    logger.warning(
                        'Discarding unreadable cache entry %r: %s', k, e)
                    try:
                        del self.index[k]
                    except Exception:
                        pass
        return d

    def load_from_dict(self, d: dict) -> None:
        self.index.clear()
        for k, v in d.items():
            self.index[k] = v

    def migrate(self, param_cache: ParamCache):
        index = param_cache.index
        for k in index:
            if '.' not in k:
                continue
            try:
                v = index[k]
            except Exception as e:
                logger.warning(
                    'Discarding unreadable cache entry %r: %s', k, e)
                try:
                    del index[k]
                except Exception:
                    pass
                continue
            main_key, *keys = k.split('.')
            if len(keys) == 0:
                self.index[main_key] = v
            else:
                d2 = value = self.index.get(main_key, {})
                if len(keys) > 1:
                    for key in keys[:-1]:
                        d2[key] = d2.get(key, {})
                        d2 = d2[key]
                d2[keys[-1]] = v
                self.index[main_key] = value

            del index[k]
            print(f'migrating {k}')
