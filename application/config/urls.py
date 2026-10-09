"""Constructores de URL de conexión SQLAlchemy."""
from urllib.parse import parse_qsl

from sqlalchemy import URL


def mssql_url(secrets: dict, application_name: str, **extra_query) -> str:
    """Cadena de conexión mssql+pyodbc a partir del bloque de secretos.

    ``secrets['params']`` es una cadena de query (p.ej.
    ``'driver=ODBC+Driver+17+...&TrustServerCertificate=yes'``) que se
    convierte a dict. ``extra_query`` añade/sobrescribe parámetros (p.ej.
    ``Mars_Connection='Yes'``).

    Se devuelve un ``str`` (y no un ``URL``) para que sea serializable al
    pasarlo como parámetro a papermill; ``str(URL)`` enmascara la
    contraseña con ``***`` y rompe la autenticación.
    """
    query = dict(parse_qsl(secrets['params'], keep_blank_values=True))
    query['APP'] = application_name
    query.update(extra_query)
    return URL.create(
        'mssql+pyodbc',
        username=secrets['user'],
        password=secrets['password'],
        host=secrets['host'],
        port=secrets['port'],
        database=secrets['dbname'],
        query=query,
    ).render_as_string(hide_password=False)


def postgres_url(
    secrets: dict, application_name: str | None = None, **extra_query
) -> str:
    """Cadena de conexión postgresql+psycopg a partir del bloque de secretos.

    Se devuelve un ``str`` (y no un ``URL``) para que sea serializable al
    pasarlo como parámetro a papermill; ``str(URL)`` enmascara la
    contraseña con ``***`` y rompe la autenticación.
    """
    query: dict[str, str] = {}
    if application_name is not None:
        query['application_name'] = application_name
    query.update(extra_query)
    return URL.create(
        'postgresql+psycopg',
        username=secrets['user'],
        password=secrets['password'],
        host=secrets['host'],
        port=secrets['port'],
        database=secrets['dbname'],
        query=query,
    ).render_as_string(hide_password=False)
