from jinja2.utils import Markup

from .config import config


class BaseWidget:
    template = "starlette_admin/partials/widget.html"

    def get_context(self):
        return {"icon": "fa fa-cog", "value": 0, "text": "Some text"}

    def render(self):
        template = config.templates.get_template(self.template)
        return template.render(self.get_context())

    @property
    def html(self):
        return Markup(self.render())
