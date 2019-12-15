# Admin Site

The [`starlette_admin.site.AdminSite`](https://github.com/accent-starlette/starlette-admin/blob/master/starlette_admin/site.py) class inherits from [`starlette.routing.Router`](https://www.starlette.io/routing/#working-with-router-instances). So when used should be treated the same.

The main differences here is that it includes additional methods such as:

```python
class AdminSite(Router):
    def register(self, model_admin) -> None:
        """ register an admin class on this site """

    def registry(self) -> typing.List["starlette_admin.admin.BaseAdmin"]:
        """
        Returns a sorted list of `starlette_admin.admin.BaseAdmin` classes
        registered on this admin
        """

    def register_widget(self, widget) -> None:
        """ register a widget on this site """

    def widgets(self) -> typing.List["starlette_admin.widgets.BaseWidget"]:
        """
        Returns a list of `starlette_admin.widgets.BaseWidget` classes
        registered on this admin
        """

    def get_logout_url(self, request) -> str:
        """ gets the logout url, by default will look for `auth:logout`.
        can be overridden if different. When set will display the logout icon """

    def get_context(self, request) -> dict:
        """ gets the default context that all endpoints will share """

    def is_auth_enabled(self, request) -> bool:
        """ attempts to see if request.user is set to be able to
        display the users display_name """

    @property
    def base_url_name(self) -> str:
        """ returns the root url of the site ie `admin:root` """

    async def root(self, request):
        """ the root view of the admin site """
```

## Initializing

There are two arguments here to take note of:

```python
def __init__(
    self,
    # name should be unique and a single word. It is used in routing
    # ie admin:root
    name: str,
    # the list of default permission scopes required
    # ie ["authenticated", "admin"]
    permission_scopes: typing.Sequence[str] = [])
```

## Registering Admin Classes

A simple example, see [`BaseAdmin`](../base_admin) for further details on creating
an admin class.

```python
class PersonAdmin(BaseAdmin):
    ...

adminsite = AdminSite(name="admin", permission_scopes=["authenticated"])

adminsite.register(PersonAdmin)
```

## Registering Widgets

See [widgets](../widgets).
