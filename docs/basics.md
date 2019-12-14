# The Basics

Once installed, getting an empty admin site shell up is simple.

```python
from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from starlette_admin.site import AdminSite

# create our admin app
adminsite = AdminSite(name="admin")

# create our starlette app
app = Starlette()

# mount the admin site to /admin
app.mount(path="/admin", app=adminsite, name=adminsite.name)

# mount the static files app, this will load js and css from `starlette_admin`
app.mount(
    path="/static",
    app=StaticFiles(directory="static", packages=["starlette_admin"]),
    name="static"
)

# add session middleware, this is the min requirement as messages are used
# like "Saved successfully"
app.add_middleware(SessionMiddleware, secret_key="secret")
```

This will allow you to go to `/admin` in your browser where you will see the basic
site operational.