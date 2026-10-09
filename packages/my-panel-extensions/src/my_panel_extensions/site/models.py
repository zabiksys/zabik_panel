import markdown
import panel as pn
import param


MARKDOWN_EXTENSIONS = ["extra", "smarty", "codehilite"]


class Application(param.Parameterized):
    """A Model of an Application

    >>> from my_panel_extensions.site.models import Application
    >>> Application(
    ...     name = "Panel",
    ...     description = "The analytics app framework to rule them all",
    ...     description_long = "Turns every dash into something lit",
    ...     url = "https://panel.holoviz.org",
    ...     thumbnail = "https://panel.holoviz.org/_static/logo_stacked.png",
    ...     tags = ["awesome", "analytics", "apps"]
    Application(name='Panel')
    """
    name = param.String(
        default="New Application",
        precedence=1,
        doc="""
        The name of the application""",
    )

    description = param.String(
        regex="^.{0,150}$",
        precedence=1,
        doc="""
        A short text introduction of max 150 characters.""",
    )

    description_long = param.String(
        precedence=1,
        doc="""
        A longer description. Can contain Markdown and HTML""",
    )

    url = param.String(precedence=2, doc="The url of the application.")

    thumbnail = param.String(precedence=2, doc="The url of a thumbnail of the application.")

    tags = param.List(
        item_type=str,
        precedence=3,
        doc="""A list of tags like 'machine-learning', 'panel', 'holoviews'.""",
    )

    def intro_section(self) -> pn.pane.HTML:
        """An panel with a text introduction to the Resource

        Returns:
            pn.pane.HTML: The Intro Section panel.
        """
        return pn.pane.HTML(self._repr_html_())

    @staticmethod
    def _markdown_to_html(text: str) -> str:
        return markdown.markdown(text, extensions=MARKDOWN_EXTENSIONS, output_format="html5")

    def _repr_html_(self):
        description = self._markdown_to_html(self.description_long)
        html = f"""<div class="pnx-resource">
        <h1 class="pnx-header">{ self.name }</h1>
        <p>{ description }</p>
        """
        tags = ", #".join(self.tags)
        if tags:
            html += "<p><strong>Tags:</strong> #" + tags.lower() + "</p>"

        html += "</div>"
        return html
