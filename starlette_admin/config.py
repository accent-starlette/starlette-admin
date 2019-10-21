import jinja2
from starlette_core.templating import Jinja2Templates


class AppConfig:
    templates: Jinja2Templates = Jinja2Templates(
        loader=jinja2.PackageLoader("starlette_admin")
    )


config = AppConfig()
