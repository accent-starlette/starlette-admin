import typing

import typesystem
from starlette.authentication import has_required_scope
from starlette.datastructures import QueryParams
from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse
from starlette.routing import Route, Router
from starlette.templating import Jinja2Templates
from starlette_core.paginator import InvalidPage, Paginator

from ..config import config
from ..exceptions import MissingSchemaError
from ..site import AdminSite


class BaseAdmin:
    """
    The base admin class for crud operations.

    Methods that require implementing:
    * get_list_objects
    * get_object
    * do_create
    * do_update
    * do_delete

    Variables:
        section_name:       The section/app name the model would natually live in.
        collection_name:    The collection/model name.
        list_field_names:   The list of fields to show on the main listing.
        templates:          Instance of `starlette.templating.Jinja2Templates` to load templates from.
        forms:              Instance of `typesystem.Jinja2Forms` to load form templates from.
        paginate_by:        The number of objects to show per page, set to `None` to disable pagination.
        paginator_class:    Built in pagination class.
        search_enabled:     Whether to show the search form at the top of the list view.
                            Seaching those objects is your responsibility within the 
                            `cls.get_list_objects` method.
        order_enabled:      Whether to render the list table headers as anchors that can be
                            clicked to toggle search order and direction. Ordering those objects
                            is your responsibility within the `cls.get_list_objects` method.
        list_template:      List template path.
        create_template:    Create template path.
        update_template:    Update template path.
        delete_template:    Delete template path.
        create_schema:      The `typesystem.Schema` used to validate a new object.
        update_schema:      The `typesystem.Schema` used to validate an existing object.
        delete_schema:      The `typesystem.Schema` used to validate a deleted object.
    """

    # general
    section_name: str = ""
    collection_name: str = ""
    # list view options
    list_field_names: typing.Sequence[str] = []
    paginate_by: typing.Optional[int] = None
    paginator_class = Paginator
    search_enabled: bool = False
    order_enabled: bool = False
    # permissions
    permission_scopes: typing.Sequence[str] = []
    # templating
    templates: Jinja2Templates = config.templates
    forms: typesystem.Jinja2Forms = config.forms
    create_template: str = "starlette_admin/create.html"
    delete_template: str = "starlette_admin/delete.html"
    list_template: str = "starlette_admin/list.html"
    update_template: str = "starlette_admin/update.html"
    # schemas
    create_schema: typing.Type[typesystem.Schema]
    delete_schema: typing.Type[typesystem.Schema]
    update_schema: typing.Type[typesystem.Schema]

    # will be set via `AdminSite.register`
    site: AdminSite

    @classmethod
    def get_global_context(cls, request):
        return {
            "base_url_name": cls.site.base_url_name,
            "url_names": cls.url_names(),
            "registry": cls.site.registry(),
            "request": request,
            "collection_name": cls.collection_name,
            "section_name": cls.section_name,
            "query_params": cls.query_params,
        }

    @classmethod
    def get_list_objects(cls, request):
        """
        Return the list of objects to render in the list view.

        Notes

        if `cls.order_enabled = True` you are responsible for returning
        the list of objects in their relevent order by using the request.query_params
        `order_by` and `order_direction`.

        Example:
            order_by = request.query_params.get("order_by", "id")
            order_direction = request.query_params.get("order_direction", "asc")
            return sorted(objects, key=lambda k: k[order_by], reverse=order_direction=="desc")

        if `cls.search_enabled = True` you are responsible for returning
        the filtered list of objects using the `request.query_param`
        `search`.

        """
        raise NotImplementedError()

    @classmethod
    def get_object(cls, request):
        raise NotImplementedError()

    @classmethod
    def get_form_values_from_object(cls, instance):
        if isinstance(instance, dict):
            return instance
        elif hasattr(instance, "to_json"):
            return instance.to_json()
        raise Exception("Form values must be a dict or implement a method `to_json`")

    @classmethod
    def do_create(cls, validated_data):
        raise NotImplementedError()

    @classmethod
    def do_delete(cls, instance, validated_data):
        raise NotImplementedError()

    @classmethod
    def do_update(cls, instance, validated_data):
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
        if not has_required_scope(request, cls.permission_scopes):
            raise HTTPException(403)

        context = cls.get_global_context(request)
        context.update(
            {
                "list_field_names": cls.list_field_names,
                "search_enabled": cls.search_enabled,
                "search": request.query_params.get("search"),
                "order_enabled": cls.order_enabled,
                "order_by": request.query_params.get("order_by"),
                "order_direction": request.query_params.get("order_direction"),
            }
        )

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
                }
            )
        else:
            context.update(
                {
                    "paginator": None,
                    "page_obj": None,
                    "is_paginated": False,
                    "list_objects": list_objects,
                }
            )

        return cls.templates.TemplateResponse(cls.list_template, context)

    @classmethod
    async def create_view(cls, request):
        if not has_required_scope(request, cls.permission_scopes):
            raise HTTPException(403)

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
        if not has_required_scope(request, cls.permission_scopes):
            raise HTTPException(403)

        if not cls.update_schema:
            raise MissingSchemaError()

        template = cls.update_template
        schema = cls.update_schema
        instance = cls.get_object(request)
        context = cls.get_global_context(request)

        if request.method == "GET":
            values = cls.get_form_values_from_object(instance)
            form = cls.forms.Form(schema, values=values)
            context.update({"form": form, "object": instance})
            return cls.templates.TemplateResponse(template, context)

        data = await request.form()
        validated_data, errors = schema.validate_or_error(data)

        if errors:
            form = cls.forms.Form(schema, values=data, errors=errors)
            context.update({"form": form, "object": instance})
            return cls.templates.TemplateResponse(template, context)

        cls.do_update(instance, validated_data)
        return RedirectResponse(request.url_for(cls.url_names()["list"]))

    @classmethod
    async def delete_view(cls, request):
        if not has_required_scope(request, cls.permission_scopes):
            raise HTTPException(403)

        if not cls.delete_schema:
            raise MissingSchemaError()

        template = cls.delete_template
        schema = cls.delete_schema
        instance = cls.get_object(request)
        context = cls.get_global_context(request)

        if request.method == "GET":
            values = cls.get_form_values_from_object(instance)
            form = cls.forms.Form(schema, values=values)
            context.update({"form": form, "object": instance})
            return cls.templates.TemplateResponse(template, context)

        data = await request.form()
        validated_data, errors = schema.validate_or_error(data)

        if errors:
            form = cls.forms.Form(schema, values=data, errors=errors)
            context.update({"form": form, "object": instance})
            return cls.templates.TemplateResponse(template, context)

        cls.do_delete(instance, validated_data)
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
    def url_names(cls):
        mount = cls.mount_name()
        return {
            "list": f"{cls.site.name}:{mount}_list",
            "create": f"{cls.site.name}:{mount}_create",
            "update": f"{cls.site.name}:{mount}_update",
            "delete": f"{cls.site.name}:{mount}_delete",
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

    @classmethod
    def query_params(cls, initial: QueryParams, **kwargs):
        """
        Update a `starlette.datastructures.QueryParams` objects
        with new values passed into kwargs.

        Usage:
            if url is `/?search=foo&page=1`
            {{ urlencode(request.query_params, page=2) }}
            would return `search=foo&page=2`
        """

        values = dict(initial)
        values.update(kwargs)
        return QueryParams(**values)
