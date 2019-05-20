from starlette.applications import Starlette

from .endpoints import Root


class AdminSite(Starlette):
    name: str = None

    def __init__(
        self, debug: bool = False, name: str = None
    ) -> None:
        super().__init__(debug, [])
        self.name = name
        # register default route
        self.add_route("/", Root, methods=["GET"], name="base")

    def register(self, model_admin):
        # set atts required on the admin class
        model_admin.app_name = self.name
        # register the routes for this section
        self.mount(model_admin.mount_point(), model_admin.routes())
