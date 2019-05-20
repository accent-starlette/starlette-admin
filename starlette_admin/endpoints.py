from os.path import join

from starlette.endpoints import HTTPEndpoint
from starlette.templating import Jinja2Templates

from .base import BaseAdminMetaclass
from .config import package_directory


templates_directory = join(package_directory, 'templates')
templates = Jinja2Templates(directory=templates_directory)


class Root(HTTPEndpoint):
    async def get(self, request):
        app = request["app"]
        template = "starlette_admin/root.html"
        context = {
            "entities_by_section": BaseAdminMetaclass.entities_by_section(),
            "request": request,
            "base_url_name": f"{app.name}:base"
        }
        return templates.TemplateResponse(template, context)
