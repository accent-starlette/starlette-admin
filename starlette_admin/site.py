import typing

from starlette.authentication import has_required_scope
from starlette.routing import Router

from .admin import BaseAdminMetaclass
from .config import config


class AdminSite(Router):
    name: str
    permission_scopes: typing.Sequence[str]

    def __init__(
        self,
        name: str,
        permission_scopes: typing.Sequence[str] = [],
        **kwargs: typing.Any,
    ) -> None:
        self.name = name
        self.permission_scopes = permission_scopes
        super().__init__(**kwargs)
        self.add_route("/", self.root, methods=["GET"], name="base")

    def register(self, model_admin):
        model_admin.app_name = self.name
        model_admin.permission_scopes = (
            model_admin.permission_scopes or self.permission_scopes
        )
        self.mount(model_admin.mount_point(), model_admin.routes())

    async def root(self, request):
        if not has_required_scope(request, self.permission_scopes):
            raise HTTPException(403)

        template = "starlette_admin/root.html"
        context = {
            "admin_classes": BaseAdminMetaclass.get_admin_classes(self.name),
            "base_url_name": f"{self.name}:base",
            "request": request,
        }

        return config.templates.TemplateResponse(template, context)
