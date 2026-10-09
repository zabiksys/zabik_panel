"""The Awesome Panel Gallery based on the Fast Components"""
# pylint: disable=line-too-long
import panel as pn
from my_panel_extensions.site import site
from my_panel_extensions.site.gallery import GalleryTemplate


APPLICATION = site.create_application(
    url="/",
    name="Galería apps",
    description="""A custom Panel template using the Fast web components""",
    description_long="""The Gallery provides a very visual overview to the applications and associated^M
    resources""",
    thumbnail="/assets/images/thumbnails/gallery.png",
)


@site.add(APPLICATION)
def view():
    """Return a GalleryTemplate"""
    pn.config.raw_css = [
        css for css in pn.config.raw_css if not css.startswith("/* CUSTOM TEMPLATE CSS */")
    ]
    return GalleryTemplate(
        site="Panel",
        title="Galería",
        description="""Galería de aplicaciones""",
        applications=site.applications,
        target="_self",
        theme="dark",
        meta_name="Bizak Panel Galería",
        meta_description="Galería de aplicaciones",
        meta_keywords=(
            "Awesome, HoloViz, Panel, Gallery, Apps, Science, Data Engineering, Data Science, "
            "Machine Learning, Python"
        ),
        meta_author="Juan Carlos Coruña",
    )


if __name__.startswith("bokeh"):
    view().servable()
