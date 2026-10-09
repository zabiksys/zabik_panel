import panel as pn
import panel_material_ui as pmui


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
        self._sidebar_column = pmui.Column(
                self._back_button,
                #pn.Spacer(sizing_mode='stretch_height'),
                pmui.Markdown(
                    f"Panel {pn.__version__}",
                    sizing_mode='stretch_width',
                    styles={
                        'color': 'gray',
                        'background-color': '#f0f0f0',
                        'padding': '10px',
                        'border-radius': '5px',
                    }))
        self.sidebar.append(self._back_button)
        
    def append_sidebar(self, obj) -> None:
        """Use this method to add objects to the sidebar instead of
        appending directly to self.sidebar. This method adds at the bottom
        the panel version."""
        if self.sidebar and self.sidebar[0] == self._back_button:
            self.sidebar.pop(0)
            self.sidebar.append(self._sidebar_column)
            
        if self.sidebar \
           and self.sidebar[0] == self._sidebar_column \
           and isinstance(self.sidebar[0], pmui.Column) \
           and len(self.sidebar[0]) >= 2:
                #self.sidebar[0][1].append(obj)
                self.sidebar[0].insert(-1, obj)
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
        self._sidebar_column = pmui.Column(
                self._back_button,
                #pn.Spacer(sizing_mode='stretch_height'),
                pmui.Markdown(
                    f"Panel {pn.__version__}",
                    sizing_mode='stretch_width',
                    styles={
                        'color': 'gray',
                        'background-color': '#f0f0f0',
                        'padding': '10px',
                        'border-radius': '5px',
                    }))
        self.sidebar.append(self._back_button)

    def append_sidebar(self, obj) -> None:
        """Use this method to add objects to the sidebar instead of
        appending directly to self.sidebar. This method adds at the bottom
        the panel version."""
        if self.sidebar and self.sidebar[0] == self._back_button:
            self.sidebar.pop(0)
            self.sidebar.append(self._sidebar_column)
            
        if self.sidebar \
           and self.sidebar[0] == self._sidebar_column \
           and isinstance(self.sidebar[0], pmui.Column) \
           and len(self.sidebar[0]) >= 2:
                #self.sidebar[0][1].append(obj)
                self.sidebar[0].insert(-1, obj)
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
        self._sidebar_column = pmui.Column(
                self._back_button,
                #pn.Spacer(sizing_mode='stretch_height'),
                pmui.Markdown(
                    f"Panel {pn.__version__}",
                    sizing_mode='stretch_width',
                    styles={
                        'color': 'gray',
                        'background-color': '#f0f0f0',
                        'padding': '10px',
                        'border-radius': '5px',
                    }))
        self.sidebar.append(self._back_button)

    def append_sidebar(self, obj) -> None:
        """Use this method to add objects to the sidebar instead of
        appending directly to self.sidebar. This method adds at the bottom
        the panel version."""
        if self.sidebar and self.sidebar[0] == self._back_button:
            self.sidebar.pop(0)
            self.sidebar.append(self._sidebar_column)
            
        if self.sidebar \
           and self.sidebar[0] == self._sidebar_column \
           and isinstance(self.sidebar[0], pmui.Column) \
           and len(self.sidebar[0]) >= 2:
                #self.sidebar[0][1].append(obj)
                self.sidebar[0].insert(-1, obj)
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
        self._sidebar_column = pmui.Column(
                self._back_button,
                #pn.Spacer(sizing_mode='stretch_height'),
                pmui.Markdown(
                    f"Panel {pn.__version__}",
                    sizing_mode='stretch_width',
                    styles={
                        'color': 'gray',
                        'background-color': '#f0f0f0',
                        'padding': '10px',
                        'border-radius': '5px',
                    }))
        self.sidebar.append(self._back_button)

    def append_sidebar(self, obj) -> None:
        """Use this method to add objects to the sidebar instead of
        appending directly to self.sidebar. This method adds at the bottom
        the panel version."""
        if self.sidebar and self.sidebar[0] == self._back_button:
            self.sidebar.pop(0)
            self.sidebar.append(self._sidebar_column)
            
        if self.sidebar \
           and self.sidebar[0] == self._sidebar_column \
           and isinstance(self.sidebar[0], pmui.Column) \
           and len(self.sidebar[0]) >= 2:
                #self.sidebar[0][1].append(obj)
                self.sidebar[0].insert(-1, obj)
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
        self._sidebar_column = pmui.Column(
                self._back_button,
                #pn.Spacer(sizing_mode='stretch_height'),
                pmui.Markdown(
                    f"Panel {pn.__version__}",
                    sizing_mode='stretch_width',
                    styles={
                        'color': 'gray',
                        'background-color': '#f0f0f0',
                        'padding': '10px',
                        'border-radius': '5px',
                    }))
        self.sidebar.append(self._back_button)

    def append_sidebar(self, obj) -> None:
        """Use this method to add objects to the sidebar instead of
        appending directly to self.sidebar. This method adds at the bottom
        the panel version."""
        if self.sidebar and self.sidebar[0] == self._back_button:
            self.sidebar.pop(0)
            self.sidebar.append(self._sidebar_column)
            
        if self.sidebar \
           and self.sidebar[0] == self._sidebar_column \
           and isinstance(self.sidebar[0], pmui.Column) \
           and len(self.sidebar[0]) >= 2:
                #self.sidebar[0][1].append(obj)
                self.sidebar[0].insert(-1, obj)
        else:
            self.sidebar.append(obj)
