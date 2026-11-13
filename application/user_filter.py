"""Filtros por usuario definidos en ``config/.secrets.yaml``.

Las claves admitidas dentro de ``users.<usuario>.filter`` son:

- ``account_manager``: códigos de ``dim_account_manager`` (Dashboard
  Comercial). Restringe el selector de KAMs y los datos.
- ``edi_partners``: códigos de ``dim_edi_partner.no_`` (Dashboard Sellout).
  Restringe el selector de clientes y los datos.
- ``extra_edi_partners``: partners adicionales para Sellout complete.
- ``product_manager``: código de ``dim_product_manager``.
- ``purchaser``: código de comprador.

Si un usuario no define una clave, no se aplica ninguna restricción.
"""
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


def user_filter_values(name: str) -> list[str]:
    """Devuelve un filtro de usuario como lista de valores.

    Acepta tanto un valor escalar (``account_manager: FREGANO``) como una
    lista (``edi_partners: [EDI0001, EDI0005]``). Devuelve una lista vacía
    cuando el filtro no está definido.
    """
    value = user_filter().get(name)
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)
