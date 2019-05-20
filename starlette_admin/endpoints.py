from starlette.endpoints import HTTPEndpoint

from .base import BaseAdminMetaclass
from .config import config


class Root(HTTPEndpoint):
    async def get(self, request):
        app = request["app"]
        template = "starlette_admin/root.html"
        context = {
            "entities_by_section": BaseAdminMetaclass.entities_by_section(),
            "request": request,
            "base_url_name": f"{app.name}:base"
        }
        return config.templates.TemplateResponse(template, context)
