"""user params."""
import json
import logging
from typing import Mapping, Any

import panel as pn
import param

from .config import param_cache2


logger = logging.getLogger(__name__)


class UserParams:

    def __init__(self):
        self._synced = []

    def _apply_stored(
            self,
            parameterized: param.Parameterized,
            params: list[str]) -> None:
        apply_params = {}
        version_index = getattr(parameterized, '__version_index__', None)
        stored_version_index = param_cache2.get(
            self._get_key(type(parameterized).__name__, '__version_index__'),
            None)
        logger.debug(f'app version index -> {version_index}, stored version index {stored_version_index}')
        if stored_version_index != version_index:
            klassname = self._get_key(type(parameterized).__name__)
            logger.debug(f'klassname {klassname}')
            if param_cache2.exists(klassname):
                param_cache2.clear(self._get_key(type(parameterized).__name__))
        for p in params:
            default = parameterized.param[p].default
            stored_param = param_cache2.get(
                self._get_key(type(parameterized).__name__, p), default)
            logger.debug(f'default param {p} -> {default}, stored param {stored_param}')
            if stored_param is not None:
                # try:
                #     v = json.loads(stored_param)
                # except Exception:
                #     v = stored_param
                # try:
                #     v = parameterized.param[p].deserialize(v)
                # except Exception:
                #     pass
                # print(f'Applying {v} to `{p}`')
                # setattr(parameterized, p, v)
                apply_params[p] = stored_param
                # setattr(parameterized, p, stored_param)
        logger.debug(f'apply_params {apply_params}')
        parameterized.param.update(**apply_params)

        # Update location if proceed
        query = {}
        """for p, parameters, _, _ in pn.state.location._synced:
            print('p', type(p),
                  'parameterized', type(parameterized),
                  'type(p)', type(p),
                  'type(parameterized)', type(parameterized),
                  )
            if (parameterized == p  # p can be a class, but parameterized is always an instance
               or (isinstance(p, type) and isinstance(parameterized, p))):
                for k, v in apply_params.items():
                    if k in parameters:
                        # query[parameters[k]] = v
                        query[k] = v"""
        #if query:
        #    print('updating query with', query)
        #    #pn.state.location._update_query(query=query)
        #print('updated', pn.state.location.search)

    def _update_params(
            self,
            *events: param.parameterized.Event,
            params: dict[str, Any] | None = None) -> None:
        serialized = params or {}
        for e in events:
            matches = [ps for o, ps, _ in self._synced if o in (e.cls, e.obj)]
            if not matches:
                continue
            owner = e.cls if e.obj is None else e.obj
            # try:
            #     val = owner.param[e.name].serialize(e.new)
            # except Exception:
            #     val = e.new
            # if not isinstance(val, str):
            #     val = json.dumps(val)
            # key = '.'.join([
            #     type(owner).__name__,
            #     e.name
            # ])
            # serialized[key] = val
            # import pdb; pdb.set_trace()
            klassname = type(owner).__name__
            key = self._get_key(klassname, e.name)
            # print(f'sync Writing to cache `{key}` -> `{repr(e.new)}`')
            param_cache2.set(key, e.new)
            param_cache2.set(
                self._get_key(klassname, '__version_index__'),
                getattr(owner, '__version_index__', None))

        # self.update_params(
        #     **{k: v for k, v in serialized.items() if v is not None})

    def update_params(
            self, **kwargs: Mapping[str, Any]) -> None:
        for p, v in kwargs.items():
            key = self._get_key(*p)
            # print(f'sync Writing to cache `{key}` -> `{repr(v)}`')
            param_cache2.set(key, v)

    def _get_key(self, *params: list[str]) -> list[str]:
        return [
            'unknown' if pn.state.user is None else json.loads(pn.state.user),
            *params]

    def sync(
            self,
            parameterized: param.Parameterized,
            parameters: list[str]) -> None:
        """Syncs the parameters of a Parameterized object with the parameters
        stored on the user."""
        watcher = parameterized.param.watch(
            self._update_params, parameters)
        self._synced.append((parameterized, parameters, watcher))

        # clear cache
        if pn.state.location and 'clear-cache' in pn.state.location.search:
            klassname = self._get_key(type(parameterized).__name__)
            if param_cache2.exists(klassname):
                param_cache2.clear(self._get_key(type(parameterized).__name__))

        self._apply_stored(parameterized, parameters)
        return
        # params = {}
        # for p in parameters:
        #     v = getattr(parameterized, p)
        #     if v is None:
        #         continue
        #     try:
        #         v = parameterized.param[p].serialize(v)
        #     except Exception:
        #         pass
        #     if not isinstance(v, str):
        #         v = json.dumps(v)
        #     key = '.'.join([type(parameterized).__name__, p])
        #     params[key] = v
        # self._update_params(params=params)


user_params = UserParams()
