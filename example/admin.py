import typesystem

import sqlalchemy as sa
from sqlalchemy import orm
from starlette.exceptions import HTTPException
from starlette_admin.admin import BaseAdmin, ModelAdmin
from starlette_core.schemas import ModelSchemaGenerator

from .models import DemoModel


# objects using the base admin that must implement
# all required methods
####################################################################


class DemoObject(dict):
    def __str__(self):
        return self["name"]


objects = [
    DemoObject({"id": id, "name": f"Record {id:02d}", "description": "Some description"})
    for id in range(1, 16)
]


class DemoSchema(typesystem.Schema):
    name = typesystem.String(title="Name")
    description = typesystem.Text(title="Description", allow_null=True)


class DemoAdmin(BaseAdmin):
    section_name = "Basic"
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
        search = request.query_params.get("search","").strip().lower()
        if cls.search_enabled and search:
            list_objects = list(
                filter(lambda obj: search in obj["name"].lower(), list_objects)
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
    def do_update(cls, instance, validated_data):
        index = objects.index(instance)
        for k, v in validated_data.items():
            instance[k] = v
        objects[index] = instance

    @classmethod
    def do_delete(cls, instance, validated_data):
        index = objects.index(instance)
        objects.pop(index)


# objects using the model admin
####################################################################

class DemoModelSchema(ModelSchemaGenerator):
    model = DemoModel
    model_fields = [
        "name",
        "description",
    ]


class DemoModelAdmin(ModelAdmin):
    section_name = "SQLAlchemy"
    collection_name = "Demos"
    model_class = DemoModel
    list_field_names = ["id", "name", "description"]
    paginate_by = 10
    order_enabled = True
    search_enabled = True
    create_schema = DemoModelSchema().schema()
    update_schema = DemoModelSchema().schema()
    delete_schema = typesystem.Schema

    @classmethod
    def get_search_results(cls, qs: orm.Query, term: str) -> orm.Query:
        return qs.filter(
            sa.or_(
                DemoModel.id == term,
                DemoModel.name.like(f"%{term}%"),
                DemoModel.description.like(f"%{term}%")
            )
        )
