from sqlalchemy import orm
from starlette_core.database import Base

from .base import BaseAdmin


class ModelAdmin(BaseAdmin):
    """ The base admin class for sqlalchemy crud operations. """

    model_class: Base

    @classmethod
    def get_default_ordering(cls, qs: orm.Query) -> orm.Query:
        return qs.order_by("id")

    @classmethod
    def get_search_results(cls, qs: orm.Query, term: str) -> orm.Query:
        raise NotImplementedError()

    @classmethod
    def get_ordered_results(
        cls, qs: orm.Query, order_by: str, order_direction: str
    ) -> orm.Query:
        if order_by and order_direction and getattr(cls.model_class, order_by):
            field = getattr(cls.model_class, order_by)
            if order_direction == "desc":
                qs = qs.order_by(field.desc())
            else:
                qs = qs.order_by(field)
        return qs

    @classmethod
    def get_list_objects(cls, request):
        qs = cls.model_class.query

        # if enabled, call `cls.get_search_results`
        search = request.query_params.get("search", "").strip().lower()
        if cls.search_enabled and search:
            qs = cls.get_search_results(qs, search)

        # if enabled, sort the results
        order_by = request.query_params.get("order_by")
        order_direction = request.query_params.get("order_direction")
        if cls.order_enabled and order_by and order_direction:
            qs = cls.get_ordered_results(qs, order_by, order_direction)
        else:
            qs = cls.get_default_ordering(qs)

        return qs.all()

    @classmethod
    def get_object(cls, request):
        id = request.path_params["id"]
        return cls.model_class.query.get_or_404(id)

    @classmethod
    async def do_create(cls, form):
        instance = cls.model_class()
        form.populate_obj(instance)
        instance.save()
        return instance

    @classmethod
    async def do_delete(cls, instance, form):
        instance.delete()

    @classmethod
    async def do_update(cls, instance, form):
        form.populate_obj(instance)
        instance.save()
        return instance
