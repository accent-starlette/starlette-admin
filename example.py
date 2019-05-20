import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from starlette_admin import BaseAdmin, AdminSite


class DemoObject(dict):
    def __str__(self):
        return self["name"]


objects = [
    DemoObject({"id": 1, "name": "Record 1", "description": "Something"}),
    DemoObject({"id": 2, "name": "Record 2", "description": "Something else"}),
    DemoObject({"id": 3, "name": "Record 3", "description": "Something more"}),
    DemoObject({"id": 4, "name": "Record 4", "description": "Whatever"}),
    DemoObject({"id": 5, "name": "Record 5", "description": "Cant be bothered"})
]


class DemoAdmin(BaseAdmin):
    section_name = "Example"
    collection_name = "Demos"
    list_field_names = ["name", "description"]

    @classmethod
    def get_list_objects(cls, request):
        """ overridden for demo purposes """
        return objects

    @classmethod
    def get_object(cls, request):
        """ overridden for demo purposes """
        id = request.path_params["id"]
        return next((x for x in objects if x["id"] == id), None)


class MoreAdmin(DemoAdmin):
    section_name = "Example"
    collection_name = "More Demos"


# create admin site
adminsite = AdminSite(name="admin")
# register admins
adminsite.register(DemoAdmin)
adminsite.register(MoreAdmin)

# create app
app = Starlette(debug=True)

app.mount(
    path="/static",
    app=StaticFiles(directory="static", packages=["starlette_admin"]),
    name="static"
)


@app.route('/')
async def homepage(request):
    return JSONResponse({'hello': 'world'})

# mount admin site
app.mount(path="/admin", app=adminsite, name=adminsite.name)

if __name__ == "__main__":
    uvicorn.run("example:app", host="0.0.0.0", port=8000, debug=True)
