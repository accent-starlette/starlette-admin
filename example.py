import typesystem
import uvicorn
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
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


class DemoSchema(typesystem.Schema):
    name = typesystem.String()
    description = typesystem.String()


class DemoAdmin(BaseAdmin):
    section_name = "Example"
    collection_name = "Demos"
    list_field_names = ["name", "description"]
    create_schema = DemoSchema

    @classmethod
    def get_list_objects(cls, request):
        """ overridden for demo purposes """
        return objects

    @classmethod
    def get_object(cls, request):
        """ overridden for demo purposes """
        id = request.path_params["id"]
        return next((x for x in objects if x["id"] == id), None)

    @classmethod
    def do_create(cls, validated_data):
        next_id = objects[-1]["id"] + 1 if objects else 1
        new_object = DemoObject(validated_data)
        new_object["id"] = next_id
        objects.append(new_object)


class MoreAdmin(DemoAdmin):
    section_name = "Example"
    collection_name = "More Demos"


# create admin site
adminsite = AdminSite(debug=True, name="admin")
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
    return PlainTextResponse("go to /admin to see the demo")

# mount admin site
app.mount(path="/admin", app=adminsite, name=adminsite.name)

if __name__ == "__main__":
    uvicorn.run("example:app", host="0.0.0.0", port=8000, debug=True)
