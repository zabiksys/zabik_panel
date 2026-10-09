from functools import wraps
from my_panel_extensions.site.models import Application
from panel.template.base import BasicTemplate
from typing import Callable, Dict

import param


class Site(param.Parameterized):
    """The Site provides meta data and functionality
    for registrering application meta data and
    views"""

    applications = param.List(
        doc="The list of applications to include in the site", constant=True)

    def __init__(self, **params):
        if "applications" not in params:
            params["applications"] = []

        super().__init__(**params)

    def create_application(  # pylint: disable=too-many-arguments
        self, **params
    ) -> Application:
        """Return an Application from specified params

        Returns:
          Application: An application
        """
        return Application(**params)

    def add(self, application: Application):
        """Registers your Application and view function
        >>> from my_panel_extensions.site.models import Application
        >>> from my_panel_extensions.site import Site
        >>> site = Site(name="awesome-panel.org")
        >>> application = site.create_application(
        ...     url="home",
        ...     name="Home",
        ...     description="The home page",
        ...     description_long="The home page of awesome-panel.org.",
        ...     thumbnail="",
        ...     tags=["Site"],
        ... )
        >>> @site.add(application)
        ... def view():
        ...     return pn.pane.Markdown("# Home")
        >>> site.applications
        [Application(name='Home')]
        >>> site.routes
        {'home': <function view at...>}
        """
        # pylint: disable=unsupported-assignment-operation
        if application.url not in [
            app.url for app in self.applications  # pylint: disable=not-an-iterable
        ]:  # pylint: disable=unsupported-membership-test
            self.applications.append(application)

        def inner_function(view):
            @wraps(view)
            def wrapper(*args, **kwargs):
                template = view(*args, **kwargs)
                if (
                    isinstance(template, BasicTemplate)
                    and template.title == template.param.title.default
                ):
                    if not self.name == application.name:
                        template.title = application.name
                    else:
                        template.title = ""
                self.register_post_view(template=template, application=application)
                return template

            application.view = wrapper
            return wrapper

        return inner_function

    # pylint: disable=unused-argument
    def register_post_view(
            self, template: BasicTemplate, application: Application):
        """Updates the template or application"""

    @property
    def routes(self) -> Dict[str, Callable]:
        """Returns a dictionary with the url as key and the view as the value

        Returns:
          Dict[str, Callable]: [description]
        """
        # pylint: disable=not-an-iterable
        return {app.url: app.view for app in self.applications}

    #
