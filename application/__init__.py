import os
from pathlib import Path
from typing import Callable

from my_panel_extensions.site import site
import yaml

from application.pages.config_file_editor import view  # noqa: F401,E501
from application.pages.export_items import view  # noqa: F401,E501
from application.pages.gallery import view  # noqa: F401
from application.pages.manage_apps import view  # noqa: F401
from application.pages.params_editor import view  # noqa: F401,E501

from application.config.config import PANEL_NOTEBOOKS_DIR


NOTEBOOKS_DIR = Path(os.environ[PANEL_NOTEBOOKS_DIR])

import importlib
import pkgutil


def import_all_views(package_path: str) -> dict:
    package_name = Path(package_path).name

    views = {}
    for importer, subname, ispkg in pkgutil.iter_modules([NOTEBOOKS_DIR]):
        if ispkg:
            subpackage_name = f'notebooks.{subname}'
            subpackage = importlib.import_module(f'{package_name}.{subname}')
            if hasattr(subpackage, 'view'):
                views[subname] = subpackage.view
                print(f'Imported view from {subpackage_name}')
    return views
 

import_all_views(NOTEBOOKS_DIR)


def notebook_apps():
    for yaml_file in NOTEBOOKS_DIR.rglob('*.yml'):
        if [p for p in yaml_file.parts if p.startswith('.')]:
            # one of the directories is hidden
            continue

        with yaml_file.open() as file:
            data = yaml.safe_load(file)
        if isinstance(data, dict) and 'url' in data:
            app = site.create_application(
                url=data['url'],
                name=data['name'],
                description=data['description'],
                description_long=data['description_long'],
                thumbnail=data['thumbnail'],
                tags=data['tags'],
            )
            app.view = str(yaml_file.parent / data['notebook'])
            site.applications.append(app)
            print(f'Appending notebook {app.view}')

notebook_apps()


APP_ROUTES: dict[str, Callable] = site.routes
