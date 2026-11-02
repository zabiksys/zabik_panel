"""Configuración de LDAP/AD desde variables de entorno ``PANELAPP_LDAP_*``.

La autenticación contra Active Directory ya no se lee de
``config/.secrets.yaml``: toda la configuración llega por variables de
entorno. Este módulo no importa Panel ni ``Config`` para poder testearse de
forma aislada.
"""
import json
import os


PREFIX = 'PANELAPP_LDAP_'

_TRUE_VALUES = {'1', 'true', 'yes', 'y', 'on', 'si', 'sí'}
_FALSE_VALUES = {'0', 'false', 'no', 'n', 'off'}


def _get(name: str) -> str | None:
    """Devuelve el valor de ``PANELAPP_LDAP_<name>`` o ``None`` si está vacío."""
    value = os.getenv(PREFIX + name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def _parse_bool(name: str, value: str | None) -> bool:
    if value is None:
        return False
    normalized = value.strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    raise RuntimeError(
        f'{PREFIX}{name} debe ser un booleano (true/false); '
        f'valor recibido: {value!r}')


def _parse_uris(value: str) -> list[str]:
    """Acepta una lista separada por comas/punto y coma o un JSON de lista."""
    value = value.strip()
    if value.startswith('['):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f'{PREFIX}URIS no es un JSON válido: {exc}') from exc
        if not isinstance(parsed, list):
            raise RuntimeError(
                f'{PREFIX}URIS debe ser una lista JSON de URIs')
        uris = [str(uri).strip() for uri in parsed]
    else:
        uris = [uri.strip() for uri in value.replace(';', ',').split(',')]
    uris = [uri for uri in uris if uri]
    if not uris:
        raise RuntimeError(f'{PREFIX}URIS no contiene ninguna URI')
    return uris


def get_ad_settings() -> dict:
    """Devuelve la configuración de AD normalizada desde el entorno.

    Variables:

    - ``PANELAPP_LDAP_DOMAIN`` (obligatoria): dominio DNS de AD.
    - ``PANELAPP_LDAP_URIS`` (obligatoria): URIs LDAP/LDAPS separadas por
      comas o punto y coma, o una lista JSON.
    - ``PANELAPP_LDAP_LOGIN_FORMAT`` (opcional): ``upn`` o ``netbios``. Si
      falta se deduce: ``netbios`` cuando el dominio no tiene punto o hay
      ``netbios_name``; ``upn`` en caso contrario.
    - ``PANELAPP_LDAP_NETBIOS_NAME`` (opcional): nombre NetBIOS del dominio.
    - ``PANELAPP_LDAP_ENCRYPT_CONNECTIONS`` (opcional): ``true``/``false``;
      por defecto ``false`` (LDAP plano, como antes).
    """
    domain = _get('DOMAIN')
    if not domain:
        raise RuntimeError(
            f'Falta la variable de entorno {PREFIX}DOMAIN '
            '(dominio DNS de Active Directory).')

    uris = _get('URIS')
    if not uris:
        raise RuntimeError(
            f'Falta la variable de entorno {PREFIX}URIS '
            '(URIs LDAP/LDAPS separadas por comas).')

    ad_config = {
        'domain': domain,
        'ldap_uris': _parse_uris(uris),
        'encrypt_connections': _parse_bool(
            'ENCRYPT_CONNECTIONS', _get('ENCRYPT_CONNECTIONS')),
    }

    netbios_name = _get('NETBIOS_NAME')
    if netbios_name:
        ad_config['netbios_name'] = netbios_name

    login_format = _get('LOGIN_FORMAT')
    if not login_format:
        if netbios_name or '.' not in domain:
            login_format = 'netbios'
        else:
            login_format = 'upn'
    login_format = login_format.lower()
    if login_format not in ('upn', 'netbios'):
        raise RuntimeError(
            f'{PREFIX}LOGIN_FORMAT debe ser "upn" o "netbios"; '
            f'valor recibido: {login_format!r}')
    ad_config['login_format'] = login_format
    return ad_config
