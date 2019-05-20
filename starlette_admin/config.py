from os.path import dirname, join, realpath

from starlette.templating import Jinja2Templates

templates_directory = join(dirname(realpath(__file__)), 'templates')


class AppConfig:
    templates = Jinja2Templates(directory=templates_directory)


config = AppConfig()
