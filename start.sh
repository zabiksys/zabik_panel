#!/usr/bin/env bash

# Carga variables locales (p. ej. BOKEH_COOKIE_SECRET) desde .env de la raíz
set -a
[ -f .env ] && . ./.env
set +a
: "${BOKEH_COOKIE_SECRET:?Define BOKEH_COOKIE_SECRET en el .env de la raíz (ver .env_dist)}"

export BOKEH_ADDRESS=0.0.0.0
export BOKEH_PORT=5006
# Bokeh compara contra el origen del navegador (host:puerto), no contra la IP
# de bind. `*:$BOKEH_PORT` permite cualquier hostname/IP en ese puerto sin
# fijar nombres propios. Si se sirve tras un proxy en otro puerto, usar '*'.
export BOKEH_ALLOW_WS_ORIGIN="*:$BOKEH_PORT"
export BOKEH_AUTH_MODULE=auth/auth.py
PANEL_CONFIG_PATH=$(realpath "config/.secrets.yaml")
export PANEL_CONFIG_PATH
PANEL_CACHE_PATH=$(realpath "config/panelindexcache")
export PANEL_CACHE_PATH
PANEL_NOTEBOOKS_DIR=$(realpath "notebooks")
export PANEL_NOTEBOOKS_DIR

#python ./app.py
uv run main.py
