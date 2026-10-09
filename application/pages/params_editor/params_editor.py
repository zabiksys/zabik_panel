"""Params editor."""
import datetime
import logging
from pprint import pformat

from my_panel_extensions.site import site
from application.config import param_cache, param_cache2

import panel as pn
import param
from template import MyMaterialTemplate


logging.basicConfig(format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# icons http://www.dna.sm/icons.html
# https://fontawesome.com/search?q=save&s=solid%2Cbrands
#  \uf0c7
APPLICATION = site.create_application(
    url='params_editor',
    name='Editar caché parámetros',
    description='',
    description_long=__doc__,
    thumbnail='/assets/images/thumbnails/params_editor.png',
    tags=['sistemas'],
)


class ParamsEditorApp(param.Parameterized):
    """Params editor."""

    editor = param.String()
    is_modified = param.String()
    error = param.String()
    success = param.Boolean(False)
    save = param.Action(label='Guardar')
    validate = param.Action(label='Validar')
    settings_panel = param.Parameter()

    def __init__(self, **params):
        super().__init__(**params)
        self.saved_params = pformat(param_cache2.dump_to_dict())
        self.editor = self.saved_params
        self.save = self._save
        self.validate = self._validate
        if 'migrate' in pn.state.location.search:
            param_cache2.migrate(param_cache)
            logger.info('Migrated from ParamCache to ParamCache2')

    def _save(self, *_):
        self.error = ''
        if self._validate():
            param_cache2.load_from_dict(
                eval(self.editor, {'datetime': datetime}))
            self.saved_params = self.editor
            self.success = True

    def _validate(self, *_):
        self.success = False
        try:
            eval(self.editor, {'datetime': datetime})
        except Exception as e:
            self.error = str(e)
            return False
        return True

    @pn.depends('error', 'success')
    def view(self) -> pn.Column:
        """Returns the view of the application

        Returns:
          pn.Column: The view of the app."""

        return pn.Column(
            pn.Param(
                self.param,
                parameters=['editor', 'is_modified', 'save'],
                widgets={
                    'editor': {
                        'type': pn.widgets.CodeEditor,
                        'language': 'python',
                    },
                    'save': {
                        'button_type': 'primary',
                        'width': 150,
                        'icon': 'device-floppy'},
                }
            ),
            pn.pane.Alert(f'## Error\n{self.error}', alert_type='danger')
            if self.error else None,
            pn.pane.Alert('Guardado', alert_type='success')
            if self.success else None,
        )


@site.add(APPLICATION)
def view() -> pn.Column:
    """returns a servable Template"""
    pn.config.sizing_mode = "stretch_width"
    app = ParamsEditorApp(name=APPLICATION.name)
    template = MyMaterialTemplate(title=APPLICATION.name)
    template.append_sidebar(pn.pane.HTML('<hr/>'))
    template.append_sidebar(app.settings_panel)
    template.main.append(app.view)
    return template


if __name__.startswith("bokeh"):
    view().servable()
