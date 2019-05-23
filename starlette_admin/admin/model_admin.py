from sqlalchemy import orm
from starlette_core.database import Base

from .base import BaseAdmin


class ModelAdmin(BaseAdmin):
    """
    The base admin class for sqlalchemy crud operations.

    Methods that require implementing:
    * get_search_results (if `cls.search_enabled = True`)

    Variables:
        section_name:       The section/app name the model would natually live in.
        collection_name:    The collection/model name.
        model_class:        The declarative base model class.
        list_field_names:   The list of fields to show on the main listing.
        templates:          Instance of `starlette.templating.Jinja2Templates` to load templates from.
        forms:              Instance of `typesystem.Jinja2Forms` to load form templates from.
        paginate_by:        The number of objects to show per page, set to `None` to disable pagination.
        paginator_class:    Built in pagination class.
        search_enabled:     Whether to show the search form at the top of the list view.
                            Seaching those objects is your responsibility within the 
                            `cls.get_list_objects` method.
        order_enabled:      Whether to render the list table headers as anchors that can be
                            clicked to toggle search order and direction. Ordering those objects
                            is your responsibility within the `cls.get_list_objects` method.
        list_template:      List template path.
        create_template:    Create template path.
        update_template:    Update template path.
        delete_template:    Delete template path.
        create_schema:      The `typesystem.Schema` used to validate a new object.
        update_schema:      The `typesystem.Schema` used to validate an existing object.
        delete_schema:      The `typesystem.Schema` used to validate a deleted object.
    """

    model_class: Base

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
        if cls.order_enabled:
            order_by = request.query_params.get("order_by", "id")
            order_direction = request.query_params.get("order_direction", "asc")
            qs = cls.get_ordered_results(qs, order_by, order_direction)

        return qs.all()

    @classmethod
    def get_object(cls, request):
        id = request.path_params["id"]
        return cls.model_class.query.get_or_404(id)

    @classmethod
    def do_create(cls, validated_data):
        object = cls.model_class()
        for key in validated_data.keys():
            if hasattr(object, key):
                setattr(object, key, getattr(validated_data, key))
        object.save()

    @classmethod
    def do_delete(cls, object, validated_data):
        object.delete()

    @classmethod
    def do_update(cls, object, validated_data):
        for key in validated_data.keys():
            if hasattr(object, key):
                setattr(object, key, getattr(validated_data, key))
        object.save()
