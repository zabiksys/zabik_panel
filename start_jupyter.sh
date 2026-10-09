#!/usr/bin/env sh

export PYTHONPATH="$(pwd)"

#jupyter lab --config=jupyter_lab_config.py --ip=0.0.0.0
PANEL_CONFIG_PATH=$(realpath "config/.secrets.yaml")
export PANEL_CONFIG_PATH
PANEL_CACHE_PATH=$(realpath "config/panelindexcache")
export PANEL_CACHE_PATH
PANEL_NOTEBOOKS_DIR=$(realpath "notebooks")
export PANEL_NOTEBOOKS_DIR
./.venv/bin/jupyter lab --config=jupyter_lab_config.py --ip=0.0.0.0

#uv tool run --with jupyter jupyter lab --config=jupyter_lab_config.py --ip=0.0.0.0
#uv tool run --from jupyter-core jupyter lab --config=jupyter_lab_config.py --ip=0.0.0.0
#PYTHONPATH="$(pwd)" uv tool run jupyter lab --config=jupyter_lab_config.py --ip=0.0.0.0
