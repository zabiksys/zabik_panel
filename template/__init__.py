import panel as pn
import panel_material_ui as pmui

from my_panel_extensions.user import USER_MENU_CSS, current_user, user_menu_html

if USER_MENU_CSS not in pn.config.raw_css:
    pn.config.raw_css.append(USER_MENU_CSS)


def _user_menu():
    """Menú de sesión: icono de usuario con el nombre y la opción de salir."""
    user = current_user()
    if not user:
        return None
    return pn.pane.HTML(user_menu_html(user), margin=0)


def _add_user_menu(template):
    """Añade el menú de sesión a la derecha del header si hay usuario."""
    menu = _user_menu()
    if menu is not None:
        template.header.append(menu)


# pn.config.loading_spinner = 'petal'
class MyMaterialTemplate(pn.template.MaterialTemplate):
    """My Material Template."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        code = """
        window.location.href="/"
        """
        self._back_button = pmui.Button(
            icon='home-2',
            name='Volver a Aplicaciones',
            button_type='default')
        self._back_button.js_on_click(code=code)
        self._sidebar_column = pmui.Column(self._back_button)
        self.sidebar.append(self._back_button)
        _add_user_menu(self)
        
    def append_sidebar(self, obj) -> None:
        """Use this method to add objects to the sidebar instead of
        appending directly to self.sidebar."""
        if self.sidebar and self.sidebar[0] == self._back_button:
            self.sidebar.pop(0)
            self.sidebar.append(self._sidebar_column)

        if self.sidebar and self.sidebar[0] == self._sidebar_column:
            self.sidebar[0].append(obj)
        else:
            self.sidebar.append(obj)


class MyFastGridTemplate(pn.template.FastGridTemplate):
    """My FastGrid Template."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        code = """
        window.location.href="/"
        """
        self._back_button = pmui.Button(
            icon='home-2',
            name='Volver a Aplicaciones',
            button_type='default')
        self._back_button.js_on_click(code=code)
        self._sidebar_column = pmui.Column(self._back_button)
        self.sidebar.append(self._back_button)
        _add_user_menu(self)

    def append_sidebar(self, obj) -> None:
        """Use this method to add objects to the sidebar instead of
        appending directly to self.sidebar."""
        if self.sidebar and self.sidebar[0] == self._back_button:
            self.sidebar.pop(0)
            self.sidebar.append(self._sidebar_column)

        if self.sidebar and self.sidebar[0] == self._sidebar_column:
            self.sidebar[0].append(obj)
        else:
            self.sidebar.append(obj)


class MyFastListTemplate(pn.template.FastListTemplate):
    """My FastList Template."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        code = """
        window.location.href="/"
        """
        self._back_button = pmui.Button(
            icon='home-2',
            name='Volver a Aplicaciones',
            button_type='default')
        self._back_button.js_on_click(code=code)
        self._sidebar_column = pmui.Column(self._back_button)
        self.sidebar.append(self._back_button)
        _add_user_menu(self)

    def append_sidebar(self, obj) -> None:
        """Use this method to add objects to the sidebar instead of
        appending directly to self.sidebar."""
        if self.sidebar and self.sidebar[0] == self._back_button:
            self.sidebar.pop(0)
            self.sidebar.append(self._sidebar_column)

        if self.sidebar and self.sidebar[0] == self._sidebar_column:
            self.sidebar[0].append(obj)
        else:
            self.sidebar.append(obj)


class MyBootstrapTemplate(pn.template.BootstrapTemplate):
    """My Bootstrap Template."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        code = """
        window.location.href="/"
        """
        self._back_button = pmui.Button(
            icon='home-2',
            name='Volver a Aplicaciones',
            button_type='default')
        self._back_button.js_on_click(code=code)
        self._sidebar_column = pmui.Column(self._back_button)
        self.sidebar.append(self._back_button)
        _add_user_menu(self)

    def append_sidebar(self, obj) -> None:
        """Use this method to add objects to the sidebar instead of
        appending directly to self.sidebar."""
        if self.sidebar and self.sidebar[0] == self._back_button:
            self.sidebar.pop(0)
            self.sidebar.append(self._sidebar_column)

        if self.sidebar and self.sidebar[0] == self._sidebar_column:
            self.sidebar[0].append(obj)
        else:
            self.sidebar.append(obj)


class MyVanillaTemplate(pn.template.VanillaTemplate):
    """My Vanilla Template."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        code = """
        window.location.href="/"
        """
        self._back_button = pmui.Button(
            icon='home-2',
            name='Volver a Aplicaciones',
            button_type='default')
        self._back_button.js_on_click(code=code)
        self._sidebar_column = pmui.Column(self._back_button)
        self.sidebar.append(self._back_button)
        _add_user_menu(self)

    def append_sidebar(self, obj) -> None:
        """Use this method to add objects to the sidebar instead of
        appending directly to self.sidebar."""
        if self.sidebar and self.sidebar[0] == self._back_button:
            self.sidebar.pop(0)
            self.sidebar.append(self._sidebar_column)

        if self.sidebar and self.sidebar[0] == self._sidebar_column:
            self.sidebar[0].append(obj)
        else:
            self.sidebar.append(obj)
