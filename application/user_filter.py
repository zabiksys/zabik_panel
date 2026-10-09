"""user filter."""
import json
from typing import Any

from application.config.config import Config
import panel as pn


def user_filter() -> dict[str, Any]:
    if pn.state.user:
        return (
            Config()['users'][json.loads(pn.state.user)].get('filter', {})
            or {}  # avoide returning None
        )
    else:
        return {}
