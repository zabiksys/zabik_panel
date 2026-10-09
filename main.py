import argparse
import os
from pathlib import Path
import platform

#from application.config.config import PANEL_CACHE_PATH, PANEL_CONFIG_PATH
from bokeh.server.auth_provider import AuthModule
from bokeh.resources import Resources
import panel as pn
from tornado.web import StaticFileHandler

from application.config.config import PANEL_NOTEBOOKS_DIR
from application.config.gdrive_oauth import GDriveCallbackHandler


def main() -> None:
    # parser = argparse.ArgumentParser(description='')
    # parser.add_argument(
    #     '-c', '--config',
    #     required=True,
    #     help='Ruta del archivo de configuración (.yaml)',
    #     metavar='CONFIGFILE')
    # parser.add_argument(
    #     '-e', '--cache',
    #     required=True,
    #     help='Ruta de la cache',
    #     metavar='CACHEDIR')
    # args = parser.parse_args()
    # config_path = Path(args.config)
    # if not config_path.exists():
    #     raise Exception(f'El archivo de configuración {config_path} no existe.')
    # # set_path(config_path.resolve())
    # os.environ[PANEL_CONFIG_PATH] = str(config_path.resolve())
    # cache_path = Path(args.cache)
    # if not cache_path.exists():
    #     raise Exception(f'La ruta de la cache {cache_path} no existe.')
    # if not cache_path.is_dir():
    #     raise Exception(f'La ruta de la cache {cache_path} no es un directorio.')
    # # set_path(config_path.resolve())
    # os.environ[PANEL_CACHE_PATH] = str(cache_path.resolve())
    
    address = os.getenv("BOKEH_ADDRESS", "0.0.0.0")
    port = int(os.getenv("BOKEH_PORT", "80"))
    auth_module_path = os.getenv("BOKEH_AUTH_MODULE")
    pn.config.js_files['flatpickr-es'] = "https://npmcdn.com/flatpickr/dist/l10n/es.js"
    #pn.config.js_files['numbro-lang'] = 'https://cdnjs.cloudflare.com/ajax/libs/numbro/2.0.5/languages.min.js'
    pn.config.js_files['numbro-lang'] = 'https://cdnjs.cloudflare.com/ajax/libs/numbro/2.0.5/languages/es-ES.min.js'

    res = Resources(
        mode='inline', version=None, root_dir=None, minified=False,
        log_level='info', root_url=None, path_versioner=None, components=None)
    res.js_raw.append('/* my javascript */  flatpickr.l10ns.es = es;  flatpickr.l10ns.default = es;')

    static_dirs = {
        'assets': './assets',
        'notebooks': str(os.environ[PANEL_NOTEBOOKS_DIR])}
    from application import APP_ROUTES  # pylint: disable=unused-import
    app_routes = APP_ROUTES
    # app_routes = {
    #     **APP_ROUTES, 'test_panel': 'application/notebooks/test_panel.ipynb'}
    extra_patterns = [
        (r"/gdrive_callback", GDriveCallbackHandler),
    ]
    if platform.system() == "Windows":
        pn.serve(app_routes, port=port, dev=False, address=address,
                 auth_provider=AuthModule(auth_module_path),
                 static_dirs=static_dirs,
                 extra_patterns=extra_patterns,
                 # admin=True,
                 resources=res, show=False)
    else:
        pn.serve(app_routes, port=port, dev=False, address=address,
                 num_procs=4, reuse_sessions=True, global_loading_spinner=True,
                 auth_provider=AuthModule(auth_module_path),
                 static_dirs=static_dirs,
                 extra_patterns=extra_patterns,
                 # admin=True,
                 resources=res, show=False)


if __name__ == "__main__":
    main()
