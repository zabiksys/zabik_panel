from functools import cache
from pathlib import Path
import warnings

from application.config.config import Config
import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


#@cache
def get_secrets(path) -> dict:
    warnings.simplefilter('default', DeprecationWarning)
    warnings.warn(
        'The function `get_secret` is deprecated. Please use `application.config.config.Config` instead.',
        category=DeprecationWarning,
        stacklevel=2)
    #with open(Path(__file__).parent.parent.parent / 'config/.secrets.yaml', 'r') as f:
    # with open(path / '.secrets.yaml', 'r') as f:
    #     s = yaml.load(f, Loader=Loader)
    return Config()._data
    # return s
