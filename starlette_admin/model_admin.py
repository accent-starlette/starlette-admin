from os.path import join

from starlette.routing import Route, Router
from starlette.templating import Jinja2Templates

from .config import package_directory


class ModelAdmin:
    section_name: str = ""
    entity_name_plural: str = ""
    list_field_names: []
    templates_dir = Jinja2Templates(directory=join(package_directory, 'templates'))
    list_template = "starlette_admin/list.html"
    create_template = "starlette_admin/create.html"
    update_template = "starlette_admin/update.html"
    delete_template = "starlette_admin/delete.html"

    @classmethod
    def get_global_context(cls, request):
        return {
            "request": request,
            "entity_name_plural": cls.entity_name_plural,
            "section_name": cls.section_name
        }

    @classmethod
    def get_list_objects(cls, request):
        return []

    @classmethod
    def get_object(cls, request):
        return {}

    @classmethod
    async def list_view(cls, request):
        context = cls.get_global_context(request)
        context.update({
            "list_objects": cls.get_list_objects(request),
            "list_field_names": cls.list_field_names
        })
        return cls.templates_dir.TemplateResponse(cls.list_template, context)

    @classmethod
    async def create_view(cls, request):
        context = cls.get_global_context(request)
        return cls.templates_dir.TemplateResponse(cls.create_template, context)

    @classmethod
    async def update_view(cls, request):
        context = cls.get_global_context(request)
        context.update({
            "object": cls.get_object(request)
        })
        return cls.templates_dir.TemplateResponse(cls.update_template, context)

    @classmethod
    async def delete_view(cls, request):
        context = cls.get_global_context(request)
        context.update({
            "object": cls.get_object(request)
        })
        return cls.templates_dir.TemplateResponse(cls.delete_template, context)

    @classmethod
    def mount_point(cls):
        base_path = cls.section_name.replace(" ", "-").lower()
        entity_path = cls.entity_name_plural.replace(" ", "-").lower()
        return f"/{base_path}/{entity_path}"

    @classmethod
    def routes(cls):
        return Router(
            [
                Route("/", endpoint=cls.list_view, methods=["GET"]),
                Route("/create", endpoint=cls.create_view, methods=["GET", "POST"]),
                Route("/{id:int}/update", endpoint=cls.update_view, methods=["GET", "POST"]),
                Route("/{id:int}/delete", endpoint=cls.delete_view, methods=["GET", "POST"])
            ]
        )
