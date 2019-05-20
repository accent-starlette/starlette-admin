import uvicorn
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
    entity_name_plural = "Demos"
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


adminsite = AdminSite()

adminsite.register(DemoAdmin)


if __name__ == "__main__":
    uvicorn.run("example:adminsite", host="0.0.0.0", port=8000, debug=True)
