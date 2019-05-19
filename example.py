import uvicorn
from starlette_admin import AdminSite, ModelAdmin


class DemoAdmin(ModelAdmin):
    entity_name = "Demos"
    section_name = "Example"


adminsite = AdminSite()

adminsite.register(DemoAdmin)


if __name__ == "__main__":
    uvicorn.run("example:adminsite", host="0.0.0.0", port=8000, debug=True)
