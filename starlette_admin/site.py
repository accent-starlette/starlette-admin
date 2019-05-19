from os.path import join
import typing
from starlette.applications import Starlette
from starlette.routing import BaseRoute
from starlette.staticfiles import StaticFiles

from .config import package_directory
from .endpoints import Root


static_directory = join(package_directory, "static")


class AdminSite(Starlette):
    def __init__(
        self, debug: bool = False, routes: typing.List[BaseRoute] = None
    ) -> None:
        super().__init__(debug, routes)
        # register default routes
        self.add_route("/", Root, methods=["GET"], name="root")
        # static files, temp till usable
        self.mount(path="/static", app=StaticFiles(directory=static_directory), name="static")


adminsite = AdminSite()
