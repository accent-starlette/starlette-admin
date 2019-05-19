from os.path import join

from starlette.endpoints import HTTPEndpoint
from starlette.templating import Jinja2Templates

from .config import package_directory


templates_directory = join(package_directory, 'templates')
templates = Jinja2Templates(directory=templates_directory)


class Root(HTTPEndpoint):
    async def get(self, request):
        template = "starlette_admin/root.html"
        context = {"request": request}
        return templates.TemplateResponse(template, context)
