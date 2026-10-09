"""Config file editor."""
from my_panel_extensions.site import site
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

import yaml
import panel as pn
import param
from template import MyMaterialTemplate

from application.config.config import Config


SECRETS_FILE = 'config/.secrets.yaml'
# icons http://www.dna.sm/icons.html
# https://fontawesome.com/search?q=save&s=solid%2Cbrands
#  \uf0c7
APPLICATION = site.create_application(
    url='config_file_editor',
    name='Editar configuración',
    description='',
    description_long=__doc__,
    thumbnail='/assets/images/thumbnails/config_file_editor.png',
    tags=['sistemas'],
)

class ConfigFileEditorApp(param.Parameterized):
    """The product tracking"""

    editor = param.String()
    is_modified = param.String()
    error = param.String()
    success = param.Boolean(False)
    save = param.Action(label='Guardar')
    validate = param.Action(label='Validar')
    settings_panel = param.Parameter()

    def __init__(self, **params):
        super().__init__(**params)
        self._config = Config()
        self.saved_yaml = open(self._config.path, 'r').read()
        #self.saved_yaml = open(SECRETS_FILE, 'r').read()
        self.editor = self.saved_yaml
        self.save = self._save
        self.validate = self._validate

    def _save(self, *_):
        self.error = ''
        if self._validate():
            open(self._config.path, 'w').write(self.editor)
            #open(SECRETS_FILE, 'w').write(self.editor)
            self.saved_yaml = self.editor
            self.success = True

    def _validate(self, *_):
        self.success = False
        try:
            yaml.load(self.editor, Loader=Loader)
        except yaml.YAMLError as e:
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
                        'language': 'yaml',
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
    app = ConfigFileEditorApp(name=APPLICATION.name)
    template = MyMaterialTemplate(title=APPLICATION.name)
    template.append_sidebar(pn.pane.HTML('<hr/>'))
    template.append_sidebar(app.settings_panel)
    template.main.append(app.view)
    return template


if __name__.startswith("bokeh"):
    view().servable()
