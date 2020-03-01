import json

import sqlalchemy as sa
from sqlalchemy import orm
from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse
from starlette.routing import Route, Router
from starlette_admin.admin import BaseAdmin, ModelAdmin
from wtforms import fields, form, validators
from wtforms_alchemy import ModelForm

from .models import DemoModel, SystemSettingsModel


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


class DemoForm(form.Form):
    name = fields.TextField(validators=[validators.required()])
    description = fields.TextAreaField()


class DemoAdmin(BaseAdmin):
    section_name = "Basic"
    collection_name = "Demos"
    list_field_names = ["name", "description"]
    paginate_by = 10
    order_enabled = True
    search_enabled = True
    create_form = DemoForm
    update_form = DemoForm
    delete_form = form.Form

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
            order_by = request.query_params.get("order_by", "name")
            order_direction = request.query_params.get("order_direction", "asc")
            list_objects = sorted(
                list_objects, key=lambda k: k[order_by], reverse=order_direction=="desc"
            )

        return list_objects

    @classmethod
    def get_object(cls, request):
        id = int(request.path_params["id"])
        try:
            return next(o for o in objects if o["id"] == id)
        except StopIteration:
            raise HTTPException(404)

    @classmethod
    async def do_create(cls, form, request):
        next_id = objects[-1]["id"] + 1 if objects else 1
        new_object = DemoObject(form.data)
        new_object["id"] = next_id
        objects.append(new_object)

    @classmethod
    async def do_update(cls, instance, form, request):
        index = objects.index(instance)
        for k, v in form.data.items():
            instance[k] = v
        objects[index] = instance

    @classmethod
    async def do_delete(cls, instance, form, request):
        index = objects.index(instance)
        objects.pop(index)


# objects using the model admin
####################################################################


class DemoModelForm(ModelForm):
    class Meta:
        model = DemoModel
        field_args = {
            "date": {
                "render_kw": {
                    "data-flatpickr": json.dumps(
                        {
                            "altInput": True,
                            "altFormat": "d/m/Y",
                            "dateFormat": "Y-m-d"
                        }
                    )
                }
            }
        }

    @classmethod
    def get_session(cls):
        from starlette_core.database import Session
        return Session()


class DemoModelAdmin(ModelAdmin):
    section_name = "SQLAlchemy"
    collection_name = "Demos"
    model_class = DemoModel
    list_field_names = ["name", "description"]
    paginate_by = 10
    order_enabled = True
    search_enabled = True
    extra_css_urls = [
        "https://cdnjs.cloudflare.com/ajax/libs/flatpickr/4.6.3/flatpickr.min.css"
    ]
    extra_js_urls = [
        "https://cdnjs.cloudflare.com/ajax/libs/flatpickr/4.6.3/flatpickr.min.js"
    ]
    create_form = DemoModelForm
    update_form = DemoModelForm
    delete_form = form.Form

    @classmethod
    def get_default_ordering(cls, qs: orm.Query) -> orm.Query:
        return qs.order_by("name")

    @classmethod
    def get_search_results(cls, qs: orm.Query, term: str) -> orm.Query:
        return qs.filter(
            sa.or_(
                DemoModel.name.ilike(f"%{term}%"),
                DemoModel.description.ilike(f"%{term}%")
            )
        )


# objects using the model admin - that act as a setting model
# there is expected to only have a single object in existance.
# here the list url acts as a redirect to a single object
####################################################################


class SystemSettingsModelForm(ModelForm):
    class Meta:
        model = SystemSettingsModel


class SystemSettingsModelAdmin(ModelAdmin):
    section_name = "Settings"
    collection_name = "System Settings"
    model_class = SystemSettingsModel
    update_form = SystemSettingsModelForm
    delete_form = form.Form

    @classmethod
    def get_object(cls, request):
        obj = cls.get_queryset().first()
        if not obj:
            obj = cls.model_class()
            obj.save()
        return obj

    @classmethod
    async def list_view(cls, request):
        instance = cls.get_object(request)
        return RedirectResponse(
            url=request.url_for(cls.url_names()["edit"], id=instance.id),
            status_code=302
        )
