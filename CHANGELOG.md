# Changelog

Todas las modificaciones notables de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y este proyecto sigue [Versionado Semántico](https://semver.org/lang/es/).

## [Unreleased]

## [1.2.0] - 2026-11-13

### Added

- `application.user_filter.user_filter_values()`: normaliza los filtros por
  usuario (escalar o lista) de `config/.secrets.yaml`.
- Documentados en `AGENTS.md` los filtros por usuario de Sellout complete,
  Dashboard comercial y Dashboard sellout.

### Changed

- Actualizado Panel 1.9.4 → 1.10.0 (Bokeh 3.10.2, panel-material-ui 0.16.7).
- `pyproject.toml`: `panel==1.10.0` y `bokeh>=3.10.0`. Se deja de declarar
  `panel-material-ui`, que llega como dependencia de Panel 1.10.
- `devops/inventory/group_vars/all/panel.yml`: versiones de app y Panel
  actualizadas (nuevo tag de imagen).

### Fixed

- `UserParams` descarta las selecciones cacheadas que ya no están entre las
  opciones válidas (por ejemplo tras un cambio de permisos), evitando el
  `ValueError` de `param.update`.

### Removed

- `requirements.txt`, `requirements_dev.txt`, `myapp/` y referencias
  obsoletas en `Dockerfile`/playbook.

## [1.1.0] - 2026-11-02

### Added

- Tests de la configuración LDAP (`tests/test_auth_settings.py`).

### Changed

- La configuración de LDAP/AD ya no se lee de `config/.secrets.yaml`: ahora
  llega por variables de entorno `PANELAPP_LDAP_*`, sin fallback a YAML.
- `start.sh` valida `PANELAPP_LDAP_DOMAIN` y `PANELAPP_LDAP_URIS` al arrancar.
- El despliegue Docker/Ansible pasa las variables `PANELAPP_LDAP_*` al
  contenedor desde el `.env` de la raíz.
- `devops/Makefile`: `make server-setup` acepta `LIMIT`, `CHECK`, `TAGS`,
  `SKIP_TAGS` y `VERBOSITY`; `make help` documenta las opciones.
- Migradas las plantillas de `template/__init__.py` (`MyMaterialTemplate`,
  `MyFastGridTemplate`, `MyFastListTemplate`, `MyBootstrapTemplate` y
  `MyVanillaTemplate`) de widgets de Panel a `panel_material_ui` (`pmui`):
  `pn.widgets.Button` → `pmui.Button`, `pn.Column` → `pmui.Column` y
  `pn.pane.Markdown` → `pmui.Markdown`. Se actualiza también el chequeo
  `isinstance(..., pn.Column)` de `append_sidebar` a `pmui.Column` (pmui.Column
  no hereda de pn.Column).
- Actualizado `notebooks/app_template.ipynb` para usar `panel_material_ui`:
  se importa `pmui`, `App.view()` devuelve `pmui.Column()` y el separador del
  sidebar usa `pmui.Divider()` en lugar de `pn.pane.HTML('<hr/>')`.

### Fixed

- `config_file_editor`: cargada la extensión `codeeditor` de Panel para que el
  editor Ace se renderice (la página quedaba en blanco).

## [1.0.1] - 2026-10-22

### Added

- Menú de sesión en el header de informes y galería: icono de usuario con el
  nombre conectado, "Acerca de..." y "Cerrar sesión".
- Diálogo "Acerca de..." con el nombre y versión de la app, Python, Panel y
  pandas. La versión se lee de `pyproject.toml` en tiempo de ejecución.
- Autenticación por LDAPS (`ldaps://host:636`) configurable mediante
  `encrypt_connections`.
- Inicio de sesión mediante UPN (`usuario@dominio`), sin depender del nombre
  NetBIOS. Se mantiene `login_format: netbios` como alternativa.
- Registro en el log de los fallos de autenticación.

### Changed

- Proyecto renombrado de `bizak-panel` a `panel-app`; versión 1.0.1.
- Imagen Docker etiquetada como
  `<app>-panel-<panel>-python-<python>`; se elimina el contador final.
- El login ya no muestra el campo de dominio ni el ejemplo `bokeh/bokeh`.
- Eliminada la etiqueta `Panel <versión>` del sidebar; la información pasa al
  diálogo "Acerca de...".
- Simplificado `append_sidebar()` de las plantillas al no tener que mantener la
  versión al final del sidebar.
- Añadida una sección de versionado en `AGENTS.md` para mantener sincronizados
  `pyproject.toml` y `devops/inventory/group_vars/all/panel.yml`.
- Compatibilidad con `config/.secrets.yaml` antiguos: si falta `login_format`
  se deduce `netbios` (dominio sin punto o con `netbios_name`) o `upn`, y si
  falta `encrypt_connections` se mantiene LDAP plano como antes.

### Fixed

- Corregido el login de AD: el formato down-level `DOMINIO\usuario` requiere el
  nombre NetBIOS (`DOMGSMNT`), no el DNS (`local.zabik`).

### Security

- Las conexiones LDAP se realizan cifradas mediante LDAPS. La validación del
  certificado del DC queda pendiente de renovar los certificados del CA interno
  a claves de al menos 2048 bits.
