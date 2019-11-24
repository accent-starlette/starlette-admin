from starlette.applications import Starlette
from starlette.authentication import AuthCredentials, AuthenticationBackend, SimpleUser
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from starlette_admin.site import AdminSite
from starlette_core.database import Database, DatabaseURL
from starlette_core.middleware import DatabaseMiddleware

from .admin import DemoAdmin, DemoModelAdmin, SystemSettingsModelAdmin
from .widgets import Today, Time, DayOfYear

class DummyAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        return AuthCredentials(["authenticated"]), SimpleUser("John Smith")


DEBUG = True

url = DatabaseURL("sqlite:///:memory:")

db = Database(url)
db.create_all()

# create an admin site
adminsite = AdminSite(name="admin", permission_scopes=["authenticated"])
# register admins
adminsite.register(DemoAdmin)
adminsite.register(DemoModelAdmin)
adminsite.register(SystemSettingsModelAdmin)
# register widgets
adminsite.register_widget(Today())
adminsite.register_widget(Time())
adminsite.register_widget(DayOfYear())

# create app
app = Starlette(debug=DEBUG)

app.mount(
    path="/static",
    app=StaticFiles(directory="static", packages=["starlette_admin"]),
    name="static"
)

app.add_middleware(AuthenticationMiddleware, backend=DummyAuthBackend())
app.add_middleware(SessionMiddleware, secret_key="secret")
app.add_middleware(DatabaseMiddleware)

# mount admin site
app.mount(path="/", app=adminsite, name=adminsite.name)
