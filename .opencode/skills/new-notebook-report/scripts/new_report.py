#!/usr/bin/env python3
"""Genera el esqueleto de un nuevo informe (notebook) de este panel.

Crea, dentro del directorio de notebooks:

    notebooks/<slug>/
    ├── <slug>.ipynb   # notebook válido (nbformat 4.5) con la estructura base
    ├── <slug>.yml     # manifiesto de auto-descubrimiento
    └── <slug>.png     # miniatura 300x200 (copia de blank.png o generada)

Uso:
    python new_report.py <slug> [--name "Panel - Mi Informe"]
                              [--url <url>] [--notebooks-dir <dir>] [--force]

El esqueleto reproduce notebooks/app_template.ipynb (5 celdas). Después hay que
implementar la lógica real en App.view() y App.settings_panel().
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import struct
import sys
import uuid
import zlib
from pathlib import Path

SLUG_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")

# --- Plantilla del notebook -------------------------------------------------

_IMPORTS = """\
from pathlib import Path
from typing import Callable

from application.user_params import user_params
import panel as pn
import param
import sqlalchemy
import panel_material_ui as pmui
from template import MyMaterialTemplate
import yaml

current_dir = Path(__file__).parent if '__file__' in globals() else Path('.')
"""

_CONFIG = """\
if (current_dir / 'config.yml').exists():
    with open(current_dir / 'config.yml', 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

APPLICATION_NAME = '__APP_NAME__'
"""

_APP_CLASS = '''\
class App(param.Parameterized):
    """App"""
    __version_index__ = 1  # increment to reset user_params

    def __init__(self, get_dwh_dburi: Callable | None = None, **params):
        super().__init__(**params)
        # Conexión a base de datos (opcional). Es perezosa: create_engine no
        # conecta hasta que se usa. Se crea solo si se pasa get_dwh_dburi.
        self.engine = (
            sqlalchemy.create_engine(get_dwh_dburi(), echo=False)
            if get_dwh_dburi is not None
            else None
        )

    def onload(self) -> None:
        if pn.state.curdoc is not None:
            # we are in a panel server, not jupyter
            user_params.sync(self, [])
        # other processing on load

    def settings_panel(self) -> pn.reactive.Reactive:
        return pn.Param(
            self,
            parameters=[
            ],
            widgets={
                # Ejemplo: mapear parámetros a widgets de panel_material_ui
                # 'mi_param': pmui.Select,
                # 'otro_param': pmui.TextInput,
            }
        )

    def view(self) -> pn.reactive.Reactive:
        return pmui.Column()
'''

_BUILD = """\
# Base de datos (opcional): cuando el informe necesite datos, descomenta el
# bloque y usa una sección que exista en config/.secrets.yaml (p.ej. 'navision').
# El helper depende del motor: mssql_url para SQL Server, postgres_url para
# PostgreSQL (application/config/urls.py).
#
# from application.config.config import Config
# from application.config.urls import mssql_url
#
# def get_dwh_dburi() -> str:
#     secrets = Config()['navision']
#     return mssql_url(secrets, APPLICATION_NAME)
#
# app = App(name=APPLICATION_NAME, get_dwh_dburi=get_dwh_dburi)

app = App(name=APPLICATION_NAME)

pn.state.onload(app.onload)

pn.config.js_files['flatpickr_i18n'] = 'https://npmcdn.com/flatpickr/dist/l10n/es.js'

if pn.state.curdoc is not None:
    # We are in a panel server
    pn.state.location.sync(app, [
    ])
"""

_TEMPLATE = """\
template = MyMaterialTemplate(title=app.name)
template.append_sidebar(pmui.Divider())
template.append_sidebar(app.settings_panel)
template.main.append(app.view)
if pn.state.curdoc is None:
    # Estamos en Jupyter: servimos el informe accesible por red.
    # address='0.0.0.0' escucha en todas las interfaces (por defecto es solo
    # localhost, inaccesible desde fuera) y websocket_origin='*' evita el 403
    # de origen al entrar por la IP/hostname. El puerto se imprime en la consola.
    template.show(address='0.0.0.0', port=0, websocket_origin='*', open=False)
else:
    template.servable()
"""


def _cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": str(uuid.uuid4()),
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def build_notebook(application_name: str) -> dict:
    """Devuelve el notebook base como dict listo para ``json.dump``."""
    cells = [
        _cell(_IMPORTS),
        _cell(_CONFIG.replace("__APP_NAME__", application_name)),
        _cell(_APP_CLASS),
        _cell(_BUILD),
        _cell(_TEMPLATE),
    ]
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.13.5",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def build_manifest(slug: str, url: str, display_name: str) -> str:
    """Devuelve el contenido del manifiesto ``<slug>.yml``."""
    return (
        f"name: {display_name}\n"
        'description: ""\n'
        'description_long: ""\n'
        f"url: {url}\n"
        f"thumbnail: /notebooks/{slug}/{slug}.png\n"
        "tags: []\n"
        f"notebook: {slug}.ipynb\n"
    )


# --- Miniatura --------------------------------------------------------------


def _png_chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def write_blank_png(path: Path, width: int = 300, height: int = 200) -> None:
    """Escribe un PNG blanco de ``width`` x ``height`` usando solo stdlib."""
    row = bytearray(b"\xff\xff\xff" * width)
    raw = bytearray()
    for _ in range(height):
        raw.append(0)  # filtro tipo 0
        raw.extend(row)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _png_chunk(b"IEND", b"")
    )
    path.write_bytes(png)


def write_thumbnail(dest: Path, notebooks_dir: Path) -> str:
    """Copia ``blank.png`` si existe; si no, genera un PNG blanco."""
    blank = notebooks_dir / "blank.png"
    if blank.is_file():
        shutil.copyfile(blank, dest)
        return "copiada de notebooks/blank.png"
    write_blank_png(dest)
    return "generada (300x200)"


# --- Utilidades -------------------------------------------------------------


def derive_display_name(slug: str) -> str:
    return " ".join(word.capitalize() for word in slug.split("_"))


def resolve_notebooks_dir(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()

    env = os.environ.get("PANEL_NOTEBOOKS_DIR")
    if env:
        return Path(env).expanduser().resolve()

    cwd = Path.cwd()
    for base in [cwd, *cwd.parents]:
        candidate = base / "notebooks"
        if (candidate / "AGENTS.md").is_file():
            return candidate.resolve()
    for base in [cwd, *cwd.parents]:
        candidate = base / "notebooks"
        if candidate.is_dir():
            return candidate.resolve()
    return (cwd / "notebooks").resolve()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera el esqueleto de un nuevo informe (notebook)."
    )
    parser.add_argument("slug", help="identificador del informe (p.ej. wms_item_availability)")
    parser.add_argument("--name", help="nombre visible (por defecto derivado del slug)")
    parser.add_argument("--url", help="ruta URL (por defecto el slug)")
    parser.add_argument("--notebooks-dir", help="directorio de notebooks")
    parser.add_argument("--force", action="store_true", help="sobrescribe si ya existe")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    slug = args.slug
    if not SLUG_RE.match(slug):
        print(
            f"error: slug inválido {slug!r}. Usa minúsculas, dígitos y '_' "
            "(p.ej. wms_item_availability).",
            file=sys.stderr,
        )
        return 2

    url = args.url or slug
    display_name = args.name or derive_display_name(slug)
    # El manifiesto usa el nombre corto; APPLICATION_NAME añade el prefijo.
    prefix = "Panel - "
    if display_name.startswith(prefix):
        display_name = display_name[len(prefix):]
    application_name = f"{prefix}{display_name}"

    notebooks_dir = resolve_notebooks_dir(args.notebooks_dir)
    app_dir = notebooks_dir / slug

    if app_dir.exists() and any(app_dir.iterdir()) and not args.force:
        print(
            f"error: {app_dir} ya existe y no está vacío (usa --force para sobrescribir).",
            file=sys.stderr,
        )
        return 1

    app_dir.mkdir(parents=True, exist_ok=True)

    notebook_path = app_dir / f"{slug}.ipynb"
    with notebook_path.open("w", encoding="utf-8") as handle:
        json.dump(build_notebook(application_name), handle, indent=1, ensure_ascii=False)
        handle.write("\n")

    manifest_path = app_dir / f"{slug}.yml"
    manifest_path.write_text(build_manifest(slug, url, display_name), encoding="utf-8")

    thumb_note = write_thumbnail(app_dir / f"{slug}.png", notebooks_dir)

    print(f"Informe creado en {app_dir}")
    print(f"  - {notebook_path.name}  (APPLICATION_NAME = {application_name!r})")
    print(f"  - {manifest_path.name}  (url={url})")
    print(f"  - {slug}.png  ({thumb_note})")
    print()
    print("Siguiente paso: implementa App.view() y App.settings_panel().")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
