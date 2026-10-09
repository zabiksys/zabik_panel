# AGENTS.md — bizak-panel

## Project Overview

Python Panel/Bokeh multi-page web dashboard. Authenticated via Active Directory. Uses `uv` as package manager with a workspace layout.

## Commands

```bash
uv sync --locked          # install deps (first run or after pyproject.toml change)
uv run main.py            # start the app (requires env vars — use start.sh)
./start.sh                # start app with all required env vars set
./start_jupyter.sh        # start Jupyter Lab for notebook development
uv run pytest             # run tests
uv run pytest tests/test_param_cache.py  # run single test file
```

## Environment Variables (required to run)

Set by `start.sh` before launching:
- `PANEL_CONFIG_PATH` → `config/.secrets.yaml` (gitignored, contains AD config, user permissions)
- `PANEL_CACHE_PATH` → `config/panelindexcache`
- `PANEL_NOTEBOOKS_DIR` → `notebooks/` (absolute path required)
- `BOKEH_ADDRESS`, `BOKEH_PORT`, `BOKEH_ALLOW_WS_ORIGIN`, `BOKEH_AUTH_MODULE`, `BOKEH_COOKIE_SECRET`

## Architecture

- **Entry point**: `main.py` → `pn.serve()` with routes from `application/__init__.py`
- **Routes**: `application/__init__.py` collects `view` callables from `application/pages/*/view.py` and auto-discovers notebooks from `notebooks/` via YAML manifests (`*.yml` with `url`, `name`, `notebook` fields)
- **Pages**: each subdirectory under `application/pages/` exports a `view` (Panel component)
- **Shared package**: `packages/my-panel-extensions/` — local workspace member providing `site` router, `ParamCache`, and other utilities
- **Auth**: `auth/auth.py` — Bokeh `AuthModule` with AD login via `ms-active-directory`
- **Config**: `Config` class reads YAML from `PANEL_CONFIG_PATH`; secrets file is gitignored
- **Static files**: `assets/` and `notebooks/` served via `static_dirs`

### Repository Pattern (export_items)

Data access is abstracted behind interfaces for future flexibility:

```
application/pages/export_items/
├── models/                      # Pure Pydantic models (no SQL knowledge)
│   ├── __init__.py
│   ├── item.py                  # Item model with Title + Field annotations
│   ├── feature.py               # Feature, FeatureQuestion, FeatureAnswer, FeatureDataType
│   ├── extended_text.py         # ExtendedText dataclass
│   ├── unit_of_measure.py       # UnitOfMeasure, UOMState
│   ├── price.py                 # Price dataclass
│   ├── cross_ref.py             # CrossRefType enum
│   └── title.py                 # Title dataclass (i18n support)
│
├── repository/                  # Data access abstraction
│   ├── interfaces.py            # IItemRepository interface
│   ├── navision_backend.py      # NavisionRepository : IItemRepository (MSSQL)
│   └── business_central.py      # Stub for future REST API implementation
│
└── export_items.py              # Panel UI using panel_material_ui widgets
```

**Models**: Pure Pydantic models with `Title` metadata for i18n. No SQL or Origin references.

**Repository Interface** (`IItemRepository`):
- `get_items(filters, fields, feature_profile) -> Iterator[Item]`
- `get_lines() -> dict[str, str]`
- `get_feature_questions(feature_profile) -> OrderedDict[int, FeatureQuestion]`

**Field Selection Persistence**: User's selected export fields are stored per-user in `ParamCache2` at key `['export_items', username, 'selected_fields']`.

### Locale System

UI text uses a `_()` translation helper with `LOCALE = 'es'` constant at module level. All user-facing strings are looked up in `TRANSLATIONS` dict.

```python
LOCALE = 'es'  # Change to 'en' for English

TRANSLATIONS = {
    'es': {'title': 'Exportar artículos', ...},
    'en': {'title': 'Export Items', ...},
}

def _(key: str, **kwargs) -> str:
    return TRANSLATIONS.get(LOCALE, {}).get(key, key)
```

## External Dependencies

- Requires `unixodbc` and `msodbcsql18` (ODBC driver) for SQL Server / Navision connectivity
- Dockerfile installs these; on Arch Linux install from AUR

## Google Drive OAuth (per-user)

Some pages let users export to their own Google Drive. This uses **per-user OAuth 2.0** — each AD user authorizes Panel once and the token is cached in a local SQLite DB (`PANEL_CACHE_PATH/gdrive_tokens.db`).

Required in `config/.secrets.yaml`:
```yaml
google_drive_oauth:
  client_id:     "YOUR_CLIENT_ID.apps.googleusercontent.com"
  client_secret: "YOUR_CLIENT_SECRET"
  redirect_uri:  "http://HOST:PORT/gdrive_callback"
  panel_base_url: "http://HOST:PORT"
```

- The *redirect_uri* must be registered exactly in the Google Cloud Console for this OAuth client.
- The callback endpoint `/gdrive_callback` is served as an `extra_pattern` by the Bokeh server (see `main.py`).
- Tokens are refreshed silently via `google.auth.transport.requests.Request()` when expired.

## Testing

- Single test file: `tests/test_param_cache.py`
- Uses pytest with temp-dir fixtures
- No CI configured

## Conventions

- Comments and docs are in Spanish
- No linter, formatter, or typechecker configured
- Python 3.13+

## Docker

```bash
docker build -t bizak-panel .
# Volumes: /app/config, /app/application/notebooks
# Default port: 5006
```
