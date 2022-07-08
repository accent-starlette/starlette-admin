# Model Admin

!!! warning "Using the `ModelAdmin`"

    This class assumes that you are using the database functionality within
    `starlette_core` and that your tables inherit from its `Base` class.
    [See docs](https://accent-starlette.github.io/starlette-core/database).

The model admin class found at [`starlette_admin.admin.ModelAdmin`](https://github.com/accent-starlette/starlette-admin/blob/master/starlette_admin/admin/model_admin.py) is a class
you can use when the entities are that of a SQLAlchemy table.
It inherits the `BaseAdmin` and provides basic functionality for most
of the core methods. such as:

- get_list_objects
- get_object
- do_create
- do_delete
- do_update 

As well as additional methods for:

- get_default_ordering
- get_ordered_results

On the most part these will usually be enough but can be overritten when required.

## Example

Below is an example of a SQLAlchemy table derived from the `starlette_core.database.Base`
class, with a `wtforms_alchemy.ModelForm` for it's validation. Pagination is handled
within the list endpoint.

```python
import sqlalchemy as sa
from sqlalchemy import orm
from starlette_admin.admin import ModelAdmin
from starlette_core.database import Base, Session
from wtforms_alchemy import ModelForm


class Person(Base):
    name = sa.Column(sa.String(), nullable=False, unique=True)

    def __str__(self):
        return self.name
        

class PersonForm(ModelForm):
    class Meta:
        model = Person

    @classmethod
    def get_session(cls):
        return Session()


class PersonAdmin(ModelAdmin):
    section_name = "General"
    collection_name = "People"
    model_class = Person
    list_field_names = ["name"]
    paginate_by = 10
    order_enabled = True
    search_enabled = True
    create_form = PersonForm
    update_form = PersonForm
    delete_form = form.Form

    @classmethod
    def get_default_ordering(cls, qs: orm.Query) -> orm.Query:
        """ the default ordering of the list """

        return qs.order_by("name")

    @classmethod
    def get_search_results(cls, qs: orm.Query, term: str) -> orm.Query:
        """ filter the qs from the search term """

        return qs.filter(Person.name.ilike(f"%{term}%"))
```

## Registering the Admin

Once created register the admin on the admin site.

```python
adminsite = AdminSite(name="admin")
adminsite.register(PersonAdmin)
```
