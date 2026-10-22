"""Utilidades para obtener el usuario de la sesión actual."""
import html
import importlib.metadata
import json
import os
import platform
import tomllib
from pathlib import Path

import panel as pn

APP_NAME = "Panel App"


def _read_pyproject_version() -> str | None:
    """Lee la versión del pyproject.toml (local o dentro del contenedor)."""
    candidates = [Path.cwd() / "pyproject.toml"]
    try:
        candidates.append(Path(__file__).resolve().parents[4] / "pyproject.toml")
    except IndexError:
        pass
    for path in candidates:
        try:
            with path.open("rb") as file:
                return str(tomllib.load(file)["project"]["version"])
        except (OSError, KeyError, tomllib.TOMLDecodeError):
            continue
    return None


def _app_version() -> str:
    """Versión de la app: env, metadatos de la distribución o pyproject.toml."""
    version = os.environ.get("PANEL_APP_VERSION")
    if version:
        return version
    try:
        return importlib.metadata.version("panel-app")
    except importlib.metadata.PackageNotFoundError:
        pass
    return _read_pyproject_version() or "desconocida"


def _package_version(package: str) -> str:
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return "desconocida"


APP_VERSION = _app_version()
PANDAS_VERSION = _package_version("pandas")


def current_user() -> str:
    """Devuelve el usuario autenticado o '' si no hay sesión.

    La cookie 'user' se guarda como JSON (ver auth/auth.py), por lo que
    pn.state.user devuelve el valor entrecomillado (p.ej. '"jcn"').
    """
    raw = pn.state.user
    if not raw:
        return ''
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return str(raw)


USER_ICON_SVG = (
    '<svg class="user-menu-icon" xmlns="http://www.w3.org/2000/svg" '
    'viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 '
    '10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 '
    '1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 '
    '1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/></svg>'
)

USER_ITEM_ICON_SVG = (
    '<svg class="user-menu-item-icon" xmlns="http://www.w3.org/2000/svg" '
    'viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4'
    '-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>'
)

LOGOUT_ICON_SVG = (
    '<svg class="user-menu-item-icon" xmlns="http://www.w3.org/2000/svg" '
    'viewBox="0 0 24 24" fill="currentColor"><path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17'
    'l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/></svg>'
)

ABOUT_ICON_SVG = (
    '<svg class="user-menu-item-icon" xmlns="http://www.w3.org/2000/svg" '
    'viewBox="0 0 24 24" fill="currentColor"><path d="M11 7h2v2h-2zm0 4h2v6h-2zm1-9C6.48 2 '
    '2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 '
    '8-8 8 3.59 8 8-3.59 8-8 8z"/></svg>'
)


def about_dialog_html(dialog_id: str = 'about-dialog') -> str:
    """Diálogo modal con la versión de la app y del entorno."""
    dialog_id = html.escape(dialog_id)
    return f"""
<dialog id="{dialog_id}" class="about-dialog">
    <h3>{APP_NAME} <span class="about-version">{html.escape(APP_VERSION)}</span></h3>
    <dl>
        <dt>Python</dt><dd>{html.escape(platform.python_version())}</dd>
        <dt>Panel</dt><dd>{html.escape(pn.__version__)}</dd>
        <dt>pandas</dt><dd>{html.escape(PANDAS_VERSION)}</dd>
    </dl>
    <form method="dialog"><button class="about-close">Cerrar</button></form>
</dialog>
"""

# CSS global: los panes HTML de Bokeh se renderizan en un shadow root, por lo
# que los estilos del menú van dentro del propio HTML (USER_MENU_HTML_STYLE).
# Aquí solo queda lo que afecta a elementos del header (spinner / toggle tema).
USER_MENU_CSS = """
#header:not(.mdc-top-app-bar):not(.navbar) { position: relative; }
#header .pn-busy-container { margin-right: 48px; }
#header .pn-toggle-theme { margin-right: 48px; }
"""

USER_MENU_HTML_STYLE = """
<style>
/* El pane HTML usa un shadow root con position: relative; lo anulamos para
   que el menú se posicione respecto al header y no respecto al pane (0x0). */
:host {
    position: static !important;
    width: 0 !important;
    height: 0 !important;
    overflow: visible !important;
}
.user-menu {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    z-index: 100;
    margin: 0;
    color: var(--header-color, #fff);
}
.user-menu > summary {
    list-style: none;
    cursor: pointer;
    outline: none;
    line-height: 1;
}
.user-menu > summary::-webkit-details-marker { display: none; }
.user-menu .user-menu-icon {
    width: 30px;
    height: 30px;
    vertical-align: middle;
    fill: currentColor;
}
.user-menu .user-menu-panel {
    position: absolute;
    right: 0;
    top: 100%;
    margin-top: 0.5em;
    padding: 0.75em 1em;
    min-width: 170px;
    background: #ffffff;
    color: #000000;
    border-radius: 6px;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.35);
    text-align: left;
    white-space: nowrap;
}
.user-menu .user-menu-item-icon {
    width: 18px;
    height: 18px;
    flex: none;
    fill: currentColor;
}
.user-menu .user-menu-name,
.user-menu .user-menu-about,
.user-menu .user-menu-logout {
    display: flex;
    align-items: center;
    gap: 0.5em;
}
.user-menu .user-menu-name {
    margin-bottom: 0.5em;
    font-weight: 600;
}
.user-menu .user-menu-separator {
    border: 0;
    border-top: 1px solid #e0e0e0;
    margin: 0.5em 0;
}
.user-menu .user-menu-about,
.user-menu .user-menu-logout {
    padding-top: 0.25em;
    color: #000000;
    text-decoration: none;
}
.user-menu .user-menu-about:hover,
.user-menu .user-menu-logout:hover { text-decoration: underline; }
.about-dialog {
    border: 0;
    border-radius: 10px;
    padding: 1.5em 2em;
    min-width: 260px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
    text-align: left;
    color: #000000;
}
.about-dialog::backdrop { background: rgba(0, 0, 0, 0.45); }
.about-dialog h3 { margin: 0 0 0.75em; }
.about-dialog .about-version {
    font-size: 0.8em;
    font-weight: 400;
    color: #555555;
    margin-left: 0.3em;
}
.about-dialog dl {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0.25em 1em;
    margin: 0 0 1.25em;
}
.about-dialog dt { color: #555555; }
.about-dialog dd { margin: 0; font-weight: 600; }
.about-dialog .about-close {
    padding: 0.4em 1.2em;
    border: 0;
    border-radius: 6px;
    background: #1565c0;
    color: #ffffff;
    cursor: pointer;
}
</style>
"""


def user_menu_html(user: str, logout_url: str = '/logout',
                   dialog_id: str = 'about-dialog') -> str:
    """HTML del desplegable de sesión (usuario, acerca de y cerrar sesión)."""
    user = html.escape(user)
    logout_url = html.escape(logout_url)
    dialog_id = html.escape(dialog_id)
    return f"""{USER_MENU_HTML_STYLE}
<details class="user-menu">
    <summary title="Sesión: {user}">{USER_ICON_SVG}</summary>
    <div class="user-menu-panel">
        <span class="user-menu-name">{USER_ITEM_ICON_SVG}{user}</span>
        <hr class="user-menu-separator">
        <a class="user-menu-about" href="#" onclick="const r=this.getRootNode(); this.closest('details.user-menu').open=false; r.querySelector('#{dialog_id}').showModal(); return false;">{ABOUT_ICON_SVG}Acerca de...</a>
        <a class="user-menu-logout" href="{logout_url}">{LOGOUT_ICON_SVG}Cerrar sesión</a>
    </div>
</details>
{about_dialog_html(dialog_id)}
"""
