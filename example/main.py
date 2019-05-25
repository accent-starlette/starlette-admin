from starlette.applications import Starlette
from starlette.authentication import AuthCredentials, AuthenticationBackend, SimpleUser
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.staticfiles import StaticFiles
from starlette_admin.config import config
from starlette_admin.site import AdminSite
from starlette_core.database import Database
from starlette_core.middleware import DatabaseMiddleware

from .admin import DemoAdmin, DemoModelAdmin


class DummyAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        return AuthCredentials(["authenticated"]), SimpleUser("John Smith")


DEBUG = True

db = Database('sqlite:///')
db.create_all()

# config
config.logout_url = '/auth/logout'

# create an admin site
adminsite = AdminSite(name="admin", permission_scopes=["authenticated"])
# register admins
adminsite.register(DemoAdmin)
adminsite.register(DemoModelAdmin)

# create app
app = Starlette(debug=DEBUG)

app.mount(
    path="/static",
    app=StaticFiles(directory="static", packages=["starlette_admin"]),
    name="static"
)

app.add_middleware(AuthenticationMiddleware, backend=DummyAuthBackend())
app.add_middleware(DatabaseMiddleware)

# mount admin site
app.mount(path="/", app=adminsite, name=adminsite.name)
