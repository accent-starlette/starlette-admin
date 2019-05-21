import typesystem
import uvicorn
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.responses import PlainTextResponse
from starlette.staticfiles import StaticFiles

from starlette_admin import BaseAdmin, AdminSite


class DemoObject(dict):
    def __str__(self):
        return self["name"]


objects = [
    DemoObject({"id": 1, "name": "Record 1", "description": "Some description"}),
    DemoObject({"id": 2, "name": "Record 2", "description": "Some description"}),
    DemoObject({"id": 3, "name": "Record 3", "description": "Some description"}),
    DemoObject({"id": 4, "name": "Record 4", "description": "Some description"}),
    DemoObject({"id": 5, "name": "Record 5", "description": "Some description"})
]


class DemoSchema(typesystem.Schema):
    name = typesystem.String()
    description = typesystem.String()


class DemoAdmin(BaseAdmin):
    section_name = "Example"
    collection_name = "Demos"
    list_field_names = ["name", "description"]
    create_schema = DemoSchema
    update_schema = DemoSchema
    delete_schema = typesystem.Schema

    @classmethod
    def get_list_objects(cls, request):
        return sorted(objects, key=lambda k: k["name"])

    @classmethod
    def get_object(cls, request):
        id = request.path_params["id"]
        try:
            return next(o for o in objects if o["id"] == id)
        except StopIteration:
            raise HTTPException(404)

    @classmethod
    def do_create(cls, validated_data):
        next_id = objects[-1]["id"] + 1 if objects else 1
        new_object = DemoObject(validated_data)
        new_object["id"] = next_id
        objects.append(new_object)

    @classmethod
    def do_update(cls, object, validated_data):
        index = objects.index(object)
        for k, v in validated_data.items():
            object[k] = v
        objects[index] = object

    @classmethod
    def do_delete(cls, object, validated_data):
        index = objects.index(object)
        objects.pop(index)


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
