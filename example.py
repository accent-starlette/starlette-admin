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
    DemoObject({"id": id, "name": f"Record {id:02d}", "description": "Some description"})
    for id in range(1, 51)
]


class DemoSchema(typesystem.Schema):
    name = typesystem.String(title="Name")
    description = typesystem.Text(title="Description")


class DemoAdmin(BaseAdmin):
    section_name = "Example"
    collection_name = "Demos"
    list_field_names = ["id", "name", "description"]
    paginate_by = 10
    order_enabled = True
    search_enabled = True
    create_schema = DemoSchema
    update_schema = DemoSchema
    delete_schema = typesystem.Schema

    @classmethod
    def get_list_objects(cls, request):
        list_objects = objects

        # if enabled, very basic search example
        search = request.query_params.get("search")
        if cls.search_enabled and search:
            list_objects = list(
                filter(lambda obj: search.lower() in obj["name"].lower(), list_objects)
            )

        # if enabled, sort the results
        if cls.order_enabled:
            order_by = request.query_params.get("order_by", "id")
            order_direction = request.query_params.get("order_direction", "asc")
            list_objects = sorted(
                list_objects, key=lambda k: k[order_by], reverse=order_direction=="desc"
            )

        return list_objects

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
