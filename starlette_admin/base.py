import typesystem
import typing
from starlette.routing import Route, Router
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from .config import config
from .exceptions import MissingSchemaError


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
    list_field_names: typing.List[str] = []
    templates: typing.Type[Jinja2Templates] = config.templates
    forms: typing.Type[typesystem.Jinja2Forms] = config.forms
    list_template: str = "starlette_admin/list.html"
    create_template: str = "starlette_admin/create.html"
    update_template: str = "starlette_admin/update.html"
    delete_template: str = "starlette_admin/delete.html"
    create_schema: typing.Type[typesystem.Schema] = None
    update_schema: typing.Type[typesystem.Schema] = None
    delete_schema: typing.Type[typesystem.Schema] = None

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
    def do_create(cls, validated_data):
        raise NotImplementedError()

    @classmethod
    def do_delete(cls, object, validated_data):
        raise NotImplementedError()

    @classmethod
    def do_update(cls, object, validated_data):
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
        if not cls.create_schema:
            raise MissingSchemaError()

        template = cls.create_template
        schema = cls.create_schema
        context = cls.get_global_context(request)

        if request.method == "GET":
            form = cls.forms.Form(schema)
            context.update({"form": form})
            return cls.templates.TemplateResponse(template, context)

        data = await request.form()
        validated_data, errors = schema.validate_or_error(data)

        if errors:
            form = cls.forms.Form(schema, values=data, errors=errors)
            context.update({"form": form})
            return cls.templates.TemplateResponse(template, context)

        cls.do_create(validated_data)
        return RedirectResponse(request.url_for(cls.url_names()["list"]))

    @classmethod
    async def update_view(cls, request):
        if not cls.update_schema:
            raise MissingSchemaError()

        template = cls.update_template
        schema = cls.update_schema
        object = cls.get_object(request)
        context = cls.get_global_context(request)

        if request.method == "GET":
            form = cls.forms.Form(schema, values=object)
            context.update({"form": form, "object": object})
            return cls.templates.TemplateResponse(template, context)

        data = await request.form()
        validated_data, errors = schema.validate_or_error(data)

        if errors:
            form = cls.forms.Form(schema, values=data, errors=errors)
            context.update({"form": form, "object": object})
            return cls.templates.TemplateResponse(template, context)

        cls.do_update(object, validated_data)
        return RedirectResponse(request.url_for(cls.url_names()["list"]))

    @classmethod
    async def delete_view(cls, request):
        if not cls.delete_schema:
            raise MissingSchemaError()

        template = cls.delete_template
        schema = cls.delete_schema
        object = cls.get_object(request)
        context = cls.get_global_context(request)

        if request.method == "GET":
            form = cls.forms.Form(schema, values=object)
            context.update({"form": form, "object": object})
            return cls.templates.TemplateResponse(template, context)

        data = await request.form()
        validated_data, errors = schema.validate_or_error(data)

        if errors:
            form = cls.forms.Form(schema, values=data, errors=errors)
            context.update({"form": form, "object": object})
            return cls.templates.TemplateResponse(template, context)

        cls.do_delete(object, validated_data)
        return RedirectResponse(request.url_for(cls.url_names()["list"]))

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
