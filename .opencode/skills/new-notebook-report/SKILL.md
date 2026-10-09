---
name: Nuevo informe (notebook)
description: |
  Crear el esqueleto de un nuevo informe/app Panel-Bokeh como notebook en
  notebooks/<slug>/ (notebook .ipynb, manifiesto .yml y miniatura). Úsalo
  cuando el usuario pida crear un nuevo informe, report, app o notebook en
  este proyecto.
---

# Crear un nuevo informe (notebook)

Este proyecto sirve informes como **notebooks Jupyter/Panel** auto-descubiertos
desde `notebooks/`. Cada informe vive en su propio directorio y se registra con
un manifiesto YAML. Sigue estos pasos para crear uno nuevo.

## 0. Contexto imprescindible

- El directorio de notebooks viene de `PANEL_NOTEBOOKS_DIR` (en `start.sh` es
  `notebooks/`, siempre ruta absoluta). El código de descubrimiento está en
  `application/__init__.py`:
  - `notebook_apps()` recorre `NOTEBOOKS_DIR.rglob('*.yml')` y, por cada YAML
    con `url`, registra una app en `site` y le asigna como vista la ruta
    `yaml_file.parent / data['notebook']`.
  - No hace falta `__init__.py` en el directorio del informe. La vista se sirve
    desde el `.ipynb`. **No añadas `__init__.py`** salvo que quieras una vista
    Python dentro de `import_all_views` (no es el caso para notebooks).
- La plantilla de referencia es `notebooks/app_template.ipynb` +
  `notebooks/app_template.yml`. Copia su estructura.
- `notebooks/*` está en `.gitignore`: los informes no se versionan salvo
  `git add -f`.

## 1. Estructura de un informe

```
notebooks/<slug>/
├── <slug>.ipynb   # el informe (5 celdas, ver §3)
├── <slug>.yml     # manifiesto de registro (ver §2)
└── <slug>.png     # miniatura 300x200 (placeholder válido)
```

El `<slug>` debe ser único, en minúsculas, con dígitos y guiones bajos
(coincide con la regex `^[a-z0-9]+(?:_[a-z0-9]+)*$`).

## 2. Manifiesto `<slug>.yml`

```yaml
name: WMS Item Availability          # nombre visible en la galería
description: ""
description_long: ""
url: wms_item_availability           # ruta URL (/wms_item_availability)
thumbnail: /notebooks/wms_item_availability/wms_item_availability.png
tags: []
notebook: wms_item_availability.ipynb
```

- `url` debe ser igual al `<slug>`.
- `thumbnail` se sirve desde el estático `/notebooks` → `<NOTEBOOKS_DIR>`.
- `notebook` es relativo al directorio del `.yml`.

## 3. Notebook `<slug>.ipynb` (5 celdas)

Réplica de `app_template.ipynb`, adaptando `APPLICATION_NAME`:

1. **Imports** — `Path`, `Callable`, `user_params`, `pn`, `param`, `sqlalchemy`,
   `pmui`, `MyMaterialTemplate`, `yaml`; y `current_dir`. Las importaciones de
   base de datos se añaden solo cuando se activa la conexión (ver §4).
   ```python
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
   ```
2. **Config opcional + nombre** — lee `config.yml` del directorio del informe si
   existe (config específica por informe) y define `APPLICATION_NAME`.
   ```python
   if (current_dir / 'config.yml').exists():
       with open(current_dir / 'config.yml', 'r', encoding='utf-8') as file:
           config = yaml.safe_load(file)

   APPLICATION_NAME = 'Panel - <Nombre visible>'
   ```
3. **Clase `App(param.Parameterized)`**:
   - `__version_index__ = 1` (increméntalo para resetear `user_params`).
   - `__init__(self, get_dwh_dburi: Callable | None = None, **params)` crea el
     engine con `sqlalchemy.create_engine(...)` **solo si** se pasa un `dburi`;
     `create_engine` es perezoso y no conecta hasta que se usa el engine.
   - `onload()` llama a `user_params.sync(self, [...])` cuando hay servidor
     (`pn.state.curdoc is not None`).
   - `settings_panel()` devuelve `pn.Param(self, parameters=[...], widgets={...})`
     con `widget_type: pmui.*` (ej. `pmui.DateRangePicker`).
   - `view()` devuelve el layout raíz (empieza con `pmui.Column()`).
4. **Construcción** — crea la `App`, `pn.state.onload`, `pn.config.js_files`
   (flatpickr i18n) y `pn.state.location.sync(app, [...])`. La conexión a BBDD
   va comentada (ver §4).
   ```python
   app = App(name=APPLICATION_NAME)

   pn.state.onload(app.onload)
   pn.config.js_files['flatpickr_i18n'] = 'https://npmcdn.com/flatpickr/dist/l10n/es.js'

   if pn.state.curdoc is not None:
       pn.state.location.sync(app, [])
   ```
5. **Plantilla** — monta el template y sirve:
   ```python
   template = MyMaterialTemplate(title=app.name)
   template.append_sidebar(pmui.Divider())
   template.append_sidebar(app.settings_panel)
   template.main.append(app.view)
   if pn.state.curdoc is None:
       # Estamos en Jupyter: servimos el informe accesible por red.
       # 0.0.0.0 escucha en todas las interfaces y websocket_origin='*' evita
       # el 403 de origen al entrar por la IP/hostname del servidor.
       template.show(address='0.0.0.0', port=0, websocket_origin='*', open=False)
   else:
       template.servable()      # estamos en el servidor Panel
   ```

## 4. Fuente de datos (opcional)

El esqueleto **no abre ninguna conexión a BBDD**: `App` acepta
`get_dwh_dburi` pero, si no se le pasa, `self.engine` queda en `None`. Así el
informe nuevo carga siempre, aunque todavía no sepas de qué base de datos
saldrán los datos.

Cuando el informe necesite datos, activa la conexión:

1. Usa una sección que **exista** en `config/.secrets.yaml` (no inventes
   nombres; en este despliegue existen `navision` y `navision_bak`). Puedes
   consultar las secciones disponibles abriendo el editor de configuración o
   con `Config()._data.keys()`.
2. Importa `Config` y el helper según el motor y pásale `get_dwh_dburi` a `App`
   (descomenta el bloque que el propio esqueleto deja preparado en la 4ª celda).

Helpers de `application/config/urls.py`:

| Helper          | Motor        | Sección típica |
| --------------- | ------------ | -------------- |
| `mssql_url`     | SQL Server   | `navision`     |
| `postgres_url`  | PostgreSQL   | (la que definas) |

Ejemplo (SQL Server / Navision), tal como queda en la celda de construcción:

```python
from application.config.config import Config
from application.config.urls import mssql_url

def get_dwh_dburi() -> str:
    secrets = Config()['navision']
    return mssql_url(secrets, APPLICATION_NAME, Mars_Connection='Yes')

app = App(name=APPLICATION_NAME, get_dwh_dburi=get_dwh_dburi)
```

## 5. Convenciones del proyecto

- **Widgets e indicadores con `panel_material_ui` (`pmui`)** siempre que sea
  posible (ver `notebooks/AGENTS.md`). `pn.widgets.Tabulator` se mantiene (no
  tiene equivalente en pmui) junto con `pn.extension('tabulator')`.
- **Plantillas de `template/`**: `MyMaterialTemplate` (u otra `My*Template`).
- **Persistencia por usuario**: `user_params.sync(self, [parámetros])` +
  `__version_index__`. También existe `application.config.param_cache2` para
  claves libres (`['app', usuario, ...]`).
- **Textos de UI** con el patrón `_()`/`TRANSLATIONS` y `LOCALE = 'es'`.
- Comentarios y documentación **en español**.
- Python 3.13+.

## 6. Scaffolding rápido (recomendado)

El script `scripts/new_report.py` genera el esqueleto completo (notebook válido,
manifiesto y miniatura) sin errores de JSON. Desde la raíz del proyecto
(`~/versa-panel`):

```bash
python .opencode/skills/new-notebook-report/scripts/new_report.py <slug> \
    --name "<Nombre visible>"
```

Opciones:

- `--name`        nombre visible **sin** el prefijo `Panel - ` (por defecto se
  deriva del slug). El script lo añade solo para `APPLICATION_NAME` y evita
  duplicarlo si ya lo incluye.
- `--url`         ruta URL (por defecto el slug).
- `--notebooks-dir`  directorio de notebooks (por defecto `PANEL_NOTEBOOKS_DIR`
  o el primer `notebooks/` encontrado subiendo desde el cwd).
- `--force`       sobrescribe si ya existe.

Después, implementa la lógica real en `App.view()` y `settings_panel`.

## 7. Checklist final

- [ ] `notebooks/<slug>/<slug>.ipynb` es JSON válido (`python -m json.tool ...`).
- [ ] `notebooks/<slug>/<slug>.yml` tiene `url`, `name`, `description`,
      `description_long`, `thumbnail`, `tags`, `notebook`.
- [ ] La ruta `thumbnail` resuelve a un fichero existente.
- [ ] `APPLICATION_NAME` coincide con el `name` del manifiesto (con prefijo
      `Panel - `).
- [ ] Widgets con `pmui`; layout con `MyMaterialTemplate`; `template.servable()`.
- [ ] Si el informe muestra datos, la fuente viene de `Config()` vía
      `postgres_url`/`mssql_url`.
- [ ] Para verificar, arranca el panel (`./start.sh`) y comprueba que la app
      aparece en la galería.
