# Changelog

Todas las modificaciones notables de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y este proyecto sigue [Versionado Semántico](https://semver.org/lang/es/).

## [Unreleased]

### Changed

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
