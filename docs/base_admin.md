# Base Admin

The base admin class found at [`starlette_admin.admin.BaseAdmin`](https://github.com/accent-starlette/starlette-admin/blob/master/starlette_admin/admin/base.py) is a class
used that all entities you need to add to the admin site will need to inherit from.

It contains all the required attributes and methods required, such as list, create,
edit, delete views as well as the templates used and routing.


## Example

Here is an example of one that stores people in memory only.

```python
from starlette.exceptions import HTTPException
from starlette_admin.admin import BaseAdmin
from wtforms import fields, form, validators


# the person object
class Person(dict):
    def __str__(self):
        # all objects should have a string method to reference
        # them in templates like {{ object }}
        return self["name"]


# create a list of people
people = [
    Person({"id": id, "name": f"Person {id}"})
    for id in range(1, 10)
]


# create a form to validate the data and to use in the 
# create and edit views
class PersonForm(form.Form):
    name = fields.TextField(validators=[validators.required()])


# define the person admin
class PersonAdmin(BaseAdmin):
    section_name = "General"
    collection_name = "People"
    routing_id_part = "{id:int}"
    list_field_names = ["name"]
    paginate_by = 10
    order_enabled = True
    search_enabled = True
    create_form = PersonForm
    update_form = PersonForm
    delete_form = form.Form

    # all the below methods are already defined in the base admin class
    # and will raise exceptions of not completed

    @classmethod
    def get_list_objects(cls, request):
        """ this is used to get the main list results. 
        in the base admin class it is responsible from sorting and filtering
        the results.
        
        The list view itself will paginate the results if cls.paginate_by
        has a value """

        list_people = people

        # very basic search example
        search = request.query_params.get("search", "").strip().lower()
        if search:
            list_people = list(
                filter(
                    lambda obj: search in obj["name"].lower(),
                    list_people
                )
            )

        # sort the results
        order_by = request.query_params.get("order_by", "name")
        order_direction = request.query_params.get("order_direction", "asc")
        list_people = sorted(
            list_people,
            key=lambda k: k[order_by],
            reverse=order_direction=="desc"
        )

        return list_people

    @classmethod
    def get_object(cls, request):
        """ get the id from the url and fint the person,
        raise a 404 if not found. this will be used
        to feed the edit and delete views """

        id = int(request.path_params["id"])
        try:
            return next(o for o in people if o["id"] == id)
        except StopIteration:
            raise HTTPException(404)

    @classmethod
    async def do_create(cls, form, request):
        """ with the cleaned form and the request we can 
        create our new person and add them to the people """

        next_id = people[-1]["id"] + 1 if people else 1
        new_person = Person(form.data)
        new_person["id"] = next_id
        people.append(new_person)

    @classmethod
    async def do_update(cls, instance, form, request):
        """ here it includes an instance which is what the 
        edit view got from get_object above. we update it and
        replace the person in people """

        index = people.index(instance)
        for k, v in form.data.items():
            instance[k] = v
        people[index] = instance

    @classmethod
    async def do_delete(cls, instance, form, request):
        """ remove the person from people """

        index = people.index(instance)
        people.pop(index)
```

## Registering the Admin

Once created register the admin on the admin site.

```python
adminsite = AdminSite(name="admin")
adminsite.register(PersonAdmin)
```