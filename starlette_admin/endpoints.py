from starlette.endpoints import HTTPEndpoint

from .base import BaseAdminMetaclass
from .config import config


class Root(HTTPEndpoint):
    async def get(self, request):
        app = request["app"]
        template = "starlette_admin/root.html"
        context = {
            "admin_classes": BaseAdminMetaclass.get_admin_classes(app.name),
            "request": request,
            "base_url_name": f"{app.name}:base",
        }
        return config.templates.TemplateResponse(template, context)
