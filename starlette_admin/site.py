import typing

from starlette.authentication import has_required_scope
from starlette.exceptions import HTTPException
from starlette.routing import NoMatchFound, Router

from .config import config


class AdminSite(Router):
    name: str
    permission_scopes: typing.Sequence[str]

    _registry = []  # type: ignore

    def __init__(
        self,
        name: str,
        permission_scopes: typing.Sequence[str] = [],
        **kwargs: typing.Any,
    ) -> None:
        self.name = name
        self.permission_scopes = permission_scopes
        super().__init__(**kwargs)
        # register the root view
        self.add_route("/", self.root, methods=["GET"], name="base")

    def register(self, model_admin) -> None:
        #  set default attrs on the model admin
        model_admin.site = self
        model_admin.permission_scopes = (
            model_admin.permission_scopes or self.permission_scopes
        )
        #  append to the registry
        self._registry.append(model_admin)
        # mount the urls
        self.mount(model_admin.mount_point(), model_admin.routes())

    def registry(
        self,
    ) -> typing.List["starlette_admin.admin.BaseAdmin"]:  # type: ignore
        """
        Returns a sorted list of `starlette_admin.admin.BaseAdmin` classes
        registered on this admin
        """

        return sorted(self._registry, key=lambda k: (k.section_name, k.collection_name))

    def get_logout_url(self, request) -> str:
        try:
            return request.url_for("auth:logout")
        except NoMatchFound:
            return ""

    def get_context(self, request) -> dict:
        return {
            "base_url_name": self.base_url_name,
            "is_auth_enabled": self.is_auth_enabled(request),
            "logout_url": self.get_logout_url(request),
            "registry": self.registry(),
            "request": request,
        }

    def is_auth_enabled(self, request) -> bool:
        try:
            return request.user is not None
        except AssertionError:
            return False

    @property
    def base_url_name(self) -> str:
        return f"{self.name}:base"

    async def root(self, request):
        if not has_required_scope(request, self.permission_scopes):
            raise HTTPException(403)

        context = self.get_context(request)
        template = "starlette_admin/root.html"
        return config.templates.TemplateResponse(template, context)
