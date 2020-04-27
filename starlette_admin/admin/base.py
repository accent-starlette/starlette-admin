import typing

from sqlalchemy.exc import IntegrityError
from starlette.authentication import has_required_scope
from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse
from starlette.routing import Route, Router
from starlette_core.messages import message
from starlette_core.paginator import InvalidPage, Paginator
from wtforms.form import Form

from ..config import config
from ..exceptions import MissingFormError
from ..site import AdminSite


class BaseAdmin:
    """ The base admin class for crud operations. """

    # general
    section_name: str = ""
    collection_name: str = ""
    # list view options
    list_field_names: typing.Sequence[str] = []
    paginate_by: typing.Optional[int] = None
    paginator_class = Paginator
    search_enabled: bool = False
    order_enabled: bool = False
    # routing
    routing_id_part: str = "{id:int}"
    # permissions
    permission_scopes: typing.Sequence[str] = []
    # templating
    create_template: str = "starlette_admin/create.html"
    delete_template: str = "starlette_admin/delete.html"
    list_template: str = "starlette_admin/list.html"
    update_template: str = "starlette_admin/update.html"
    # static includes
    extra_css_urls: typing.List[str] = []
    extra_js_urls: typing.List[str] = []
    # forms
    create_form: Form
    delete_form: Form
    update_form: Form

    # will be set via `AdminSite.register`
    site: AdminSite

    @classmethod
    def get_context(cls, request):
        context = cls.site.get_context(request)
        context.update(
            {
                "collection_name": cls.collection_name,
                "section_name": cls.section_name,
                "url_names": cls.url_names(),
                "extra_css_urls": cls.extra_css_urls,
                "extra_js_urls": cls.extra_js_urls,
            }
        )
        return context

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
    async def do_create(cls, form, request):
        raise NotImplementedError()

    @classmethod
    async def do_delete(cls, instance, form, request):
        raise NotImplementedError()

    @classmethod
    async def do_update(cls, instance, form, request):
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
    def get_form(cls, form_cls: Form, **kwargs: typing.Any):
        return form_cls(**kwargs)

    @classmethod
    async def has_required_scope(cls, request):
        return has_required_scope(request, cls.permission_scopes)

    @classmethod
    async def list_view(cls, request):
        if not await cls.has_required_scope(request):
            raise HTTPException(403)

        context = cls.get_context(request)
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

        return config.templates.TemplateResponse(cls.list_template, context)

    @classmethod
    async def create_view(cls, request):
        if not await cls.has_required_scope(request):
            raise HTTPException(403)

        if not cls.create_form:
            raise MissingFormError()

        context = cls.get_context(request)

        if request.method == "GET":
            form = cls.get_form(cls.create_form)
            context.update({"form": form})
            return config.templates.TemplateResponse(cls.create_template, context)

        data = await request.form()
        form = cls.get_form(cls.create_form, formdata=data)

        if not form.validate():
            context.update({"form": form})
            return config.templates.TemplateResponse(cls.create_template, context)

        await cls.do_create(form, request)

        message(request, "Created successfully", "success")

        return RedirectResponse(
            url=request.url_for(cls.url_names()["list"]), status_code=302
        )

    @classmethod
    async def update_view(cls, request):
        if not await cls.has_required_scope(request):
            raise HTTPException(403)

        if not cls.update_form:
            raise MissingFormError()

        instance = cls.get_object(request)
        context = cls.get_context(request)
        form_kwargs = {
            "form_cls": cls.update_form,
            "data": instance if isinstance(instance, dict) else None,
            "obj": instance if not isinstance(instance, dict) else None,
        }

        if request.method == "GET":
            form = cls.get_form(**form_kwargs)
            context.update({"form": form, "object": instance})
            return config.templates.TemplateResponse(cls.update_template, context)

        data = await request.form()
        form = cls.get_form(**form_kwargs, formdata=data)

        if not form.validate():
            context.update({"form": form, "object": instance})
            return config.templates.TemplateResponse(cls.update_template, context)

        await cls.do_update(instance, form, request)

        message(request, "Updated successfully", "success")

        return RedirectResponse(
            url=request.url_for(cls.url_names()["list"]), status_code=302
        )

    @classmethod
    async def delete_view(cls, request):
        if not await cls.has_required_scope(request):
            raise HTTPException(403)

        if not cls.delete_form:
            raise MissingFormError()

        instance = cls.get_object(request)
        context = cls.get_context(request)
        form_kwargs = {
            "form_cls": cls.delete_form,
            "data": instance if isinstance(instance, dict) else None,
            "obj": instance if not isinstance(instance, dict) else None,
        }

        if request.method == "GET":
            form = cls.get_form(**form_kwargs)
            context.update({"form": form, "object": instance})
            return config.templates.TemplateResponse(cls.delete_template, context)

        data = await request.form()
        form = cls.get_form(**form_kwargs, formdata=data)

        if not form.validate():
            context.update({"form": form, "object": instance})
            return config.templates.TemplateResponse(cls.delete_template, context)

        try:
            await cls.do_delete(instance, form, request)
            message(request, "Deleted successfully", "success")
        except IntegrityError:
            message(
                request,
                "Could not be deleted due to being referenced by a related object",
                "error",
            )

        return RedirectResponse(
            url=request.url_for(cls.url_names()["list"]), status_code=302
        )

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
            "edit": f"{cls.site.name}:{mount}_edit",
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
                    f"/{cls.routing_id_part}/edit",
                    endpoint=cls.update_view,
                    methods=["GET", "POST"],
                    name=f"{mount}_edit",
                ),
                Route(
                    f"/{cls.routing_id_part}/delete",
                    endpoint=cls.delete_view,
                    methods=["GET", "POST"],
                    name=f"{mount}_delete",
                ),
            ]
        )
