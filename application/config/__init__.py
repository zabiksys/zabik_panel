from functools import partial
import os
from pathlib import Path
import warnings

from application.config.config import Config
from application.config.config import PANEL_CACHE_PATH, PANEL_CONFIG_PATH
from .get_secrets import get_secrets
from my_panel_extensions.param_cache import ParamCache
from my_panel_extensions.param_cache import ParamCache2


config_path = Path(os.environ[PANEL_CONFIG_PATH])
def secrets():
    warnings.simplefilter('default', DeprecationWarning)
    warnings.warn(
        'The function `secrets` is deprecated. Please use `application.config.config.Config` instead.',
        category=DeprecationWarning,
        stacklevel=2)
    return Config()._data

param_cache = ParamCache(os.environ[PANEL_CACHE_PATH])
param_cache2 = ParamCache2(os.environ[PANEL_CACHE_PATH])
