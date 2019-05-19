from os.path import join

from starlette.routing import Route, Router
from starlette.templating import Jinja2Templates

from .config import package_directory


class ModelAdmin:
    entity_name: str = ""
    section_name: str = ""
    templates_dir = Jinja2Templates(directory=join(package_directory, 'templates'))
    list_template = "starlette_admin/list.html"
    create_template = "starlette_admin/create.html"
    update_template = "starlette_admin/update.html"
    delete_template = "starlette_admin/delete.html"

    @classmethod
    async def list(cls, request):
        context = {"request": request}
        return cls.templates_dir.TemplateResponse(cls.list_template, context)

    @classmethod
    async def create(cls, request):
        context = {"request": request}
        return cls.templates_dir.TemplateResponse(cls.create_template, context)

    @classmethod
    async def update(cls, request):
        context = {"request": request}
        return cls.templates_dir.TemplateResponse(cls.update_template, context)

    @classmethod
    async def delete(cls, request):
        context = {"request": request}
        return cls.templates_dir.TemplateResponse(cls.delete_template, context)

    @classmethod
    def mount_point(cls):
        base_path = cls.section_name.replace(" ", "-").lower()
        entity_path = cls.entity_name.replace(" ", "-").lower()
        return f"/{base_path}/{entity_path}"

    @classmethod
    def routes(cls):
        return Router(
            [
                Route("/", endpoint=cls.list, methods=["GET"]),
                Route("/create", endpoint=cls.create, methods=["GET"]),
                Route("/{id:int}/update", endpoint=cls.update, methods=["GET"]),
                Route("/{id:int}/delete", endpoint=cls.delete, methods=["GET"])
            ]
        )
