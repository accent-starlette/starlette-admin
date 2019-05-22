import typing

import typesystem
from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse
from starlette.routing import Route, Router
from starlette.templating import Jinja2Templates
from starlette_core.paginator import InvalidPage, Paginator

from .config import config
from .exceptions import MissingSchemaError


class BaseAdminMetaclass(type):
    _registry: typing.List["BaseAdmin"] = []

    def __init__(cls, name, bases, dct):
        if not cls.__module__.startswith("__"):
            cls._registry.append(cls)
        return super().__init__(name, bases, dct)

    @classmethod
    def get_admin_classes(cls, app_name):
        for_admin = [c for c in cls._registry if c.app_name == app_name]
        return sorted(for_admin, key=lambda k: (k.section_name, k.collection_name))


class BaseAdmin(metaclass=BaseAdminMetaclass):
    """
    The base admin class for crud operations.

    Methods that require implementing:
    - get_list_objects
    - get_object
    - do_create
    - do_update
    - do_delete

    Class variables:
        section_name:       The section/app name the model would natually live in.
        collection_name:    The collection/model name.
        list_field_names:   The list of fields to show on the main listing.
        templates:          Instance of `starlette.templating.Jinja2Templates` to load templates from.
        forms:              Instance of `typesystem.Jinja2Forms` to load form templates from.
        paginate_by:        The number of objects to show per page, set to `None` to disable pagination.
        paginator_class:    Built in pagination class.
        list_template:      List template path.
        create_template:    Create template path.
        update_template:    Update template path.
        delete_template:    Delete template path.
        create_schema:      The `typesystem.Schema` used to validate a new object.
        update_schema:      The `typesystem.Schema` used to validate an existing object.
        delete_schema:      The `typesystem.Schema` used to validate a deleted object.
    """

    section_name: str = ""
    collection_name: str = ""
    list_field_names: typing.List[str] = []
    templates: Jinja2Templates = config.templates
    forms: typesystem.Jinja2Forms = config.forms
    paginate_by: typing.Optional[int] = None
    paginator_class = Paginator
    list_template: str = "starlette_admin/list.html"
    create_template: str = "starlette_admin/create.html"
    update_template: str = "starlette_admin/update.html"
    delete_template: str = "starlette_admin/delete.html"
    create_schema: typing.Type[typesystem.Schema]
    update_schema: typing.Type[typesystem.Schema]
    delete_schema: typing.Type[typesystem.Schema]

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
            "section_name": cls.section_name,
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
    def paginate(cls, request, objects):
        paginator = cls.paginator_class(objects, cls.paginate_by)
        page_number = request.query_params.get("page")

        try:
            page_number = int(page_number)
        except (TypeError, ValueError):
            page_number = 1

        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages)
        except InvalidPage as e:
            raise HTTPException(404, f"Invalid page {page_number}: {str(e)}")

    @classmethod
    async def list_view(cls, request):
        context = cls.get_global_context(request)
        list_objects = cls.get_list_objects(request)
        if cls.paginate_by:
            paginator, page, list_objects, is_paginated = cls.paginate(
                request, list_objects
            )
            context.update(
                {
                    "paginator": paginator,
                    "page_obj": page,
                    "is_paginated": is_paginated,
                    "list_objects": list_objects,
                    "list_field_names": cls.list_field_names,
                }
            )
        else:
            context.update(
                {
                    "paginator": None,
                    "page_obj": None,
                    "is_paginated": False,
                    "list_objects": list_objects,
                    "list_field_names": cls.list_field_names,
                }
            )
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
                    "/", endpoint=cls.list_view, methods=["GET"], name=f"{mount}_list"
                ),
                Route(
                    "/create",
                    endpoint=cls.create_view,
                    methods=["GET", "POST"],
                    name=f"{mount}_create",
                ),
                Route(
                    "/{id:int}/update",
                    endpoint=cls.update_view,
                    methods=["GET", "POST"],
                    name=f"{mount}_update",
                ),
                Route(
                    "/{id:int}/delete",
                    endpoint=cls.delete_view,
                    methods=["GET", "POST"],
                    name=f"{mount}_delete",
                ),
            ]
        )
