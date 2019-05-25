from os.path import dirname, join, realpath

from starlette.templating import Jinja2Templates
from starlette_core.forms import Jinja2Forms

templates_directory = join(dirname(realpath(__file__)), "templates")


class AppConfig:
    forms: Jinja2Forms = Jinja2Forms(directory=templates_directory)
    logout_url = ""
    templates: Jinja2Templates = Jinja2Templates(directory=templates_directory)


config = AppConfig()
