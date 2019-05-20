from starlette.routing import Route, Router

from .config import config


class BaseAdminMetaclass(type):
    _registry = []

    def __init__(cls, name, bases, dct):
        if not cls.__module__.startswith("__"):
            cls._registry.append(cls)
        return super().__init__(name, bases, dct)

    @classmethod
    def get_admin_classes(cls, app_name):
        for_admin = [c for c in cls._registry if c.app_name == app_name]
        return sorted(for_admin, key=lambda k: (k.section_name, k.collection_name))


class BaseAdmin(metaclass=BaseAdminMetaclass):
    section_name: str = ""
    collection_name: str = ""
    list_field_names: []
    templates = config.templates
    list_template = "starlette_admin/list.html"
    create_template = "starlette_admin/create.html"
    update_template = "starlette_admin/update.html"
    delete_template = "starlette_admin/delete.html"

    # will be set via `AdminSite.register`
    app_name = ""

    @classmethod
    def get_global_context(cls, request):
        return {
            "base_url_name": cls.base_url_name(),
            "url_names": cls.url_names(),
            "admin_classes": cls.get_admin_classes(cls.app_name),
            "request": request,
            "collection_name": cls.collection_name,
            "section_name": cls.section_name
        }

    @classmethod
    def get_list_objects(cls, request):
        raise NotImplementedError()

    @classmethod
    def get_object(cls, request):
        raise NotImplementedError()

    @classmethod
    async def list_view(cls, request):
        context = cls.get_global_context(request)
        context.update({
            "list_objects": cls.get_list_objects(request),
            "list_field_names": cls.list_field_names
        })
        return cls.templates.TemplateResponse(cls.list_template, context)

    @classmethod
    async def create_view(cls, request):
        context = cls.get_global_context(request)
        return cls.templates.TemplateResponse(cls.create_template, context)

    @classmethod
    async def update_view(cls, request):
        context = cls.get_global_context(request)
        context.update({
            "object": cls.get_object(request)
        })
        return cls.templates.TemplateResponse(cls.update_template, context)

    @classmethod
    async def delete_view(cls, request):
        context = cls.get_global_context(request)
        context.update({
            "object": cls.get_object(request)
        })
        return cls.templates.TemplateResponse(cls.delete_template, context)

    @classmethod
    def section_path(cls):
        return cls.section_name.replace(" ", "").lower()

    @classmethod
    def collection_path(cls):
        return cls.collection_name.replace(" ", "").lower()

    @classmethod
    def mount_point(cls):
        return f"/{cls.section_path()}/{cls.collection_path()}"

    @classmethod
    def mount_name(cls):
        return f"{cls.section_path()}_{cls.collection_path()}"

    @classmethod
    def base_url_name(cls):
        return f"{cls.app_name}:base"

    @classmethod
    def url_names(cls):
        mount = cls.mount_name()
        return {
            "list": f"{cls.app_name}:{mount}_list",
            "create": f"{cls.app_name}:{mount}_create",
            "update": f"{cls.app_name}:{mount}_update",
            "delete": f"{cls.app_name}:{mount}_delete",
        }

    @classmethod
    def routes(cls):
        mount = cls.mount_name()
        return Router(
            [
                Route(
                    "/",
                    endpoint=cls.list_view,
                    methods=["GET"],
                    name=f"{mount}_list"
                ),
                Route(
                    "/create",
                    endpoint=cls.create_view,
                    methods=["GET", "POST"],
                    name=f"{mount}_create"
                ),
                Route(
                    "/{id:int}/update",
                    endpoint=cls.update_view,
                    methods=["GET", "POST"],
                    name=f"{mount}_update"
                ),
                Route(
                    "/{id:int}/delete",
                    endpoint=cls.delete_view,
                    methods=["GET", "POST"],
                    name=f"{mount}_delete"
                )
            ]
        )
