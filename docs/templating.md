# Templating

If you need to replace any templates you can. Assuming you have a 
template you want to use for your `PersonAdmin.list_view`. This can be achieved
by setting:

```python
class PersonAdmin(...):
    ...
    create_template: str = "starlette_admin/create.html"  # the default
    delete_template: str = "starlette_admin/delete.html"  # the default
    list_template: str = "my_admin/list.html"
    update_template: str = "starlette_admin/update.html"  # the default
```

Also you will need to pass to `starlette_admin` your `Jinja2Templates` loader.

```python
import jinja2
from starlette_admin import config
from starlette_core.templating import Jinja2Templates

templates = Jinja2Templates(
    loader=jinja2.ChoiceLoader(
        [
            jinja2.FileSystemLoader("templates"),
            jinja2.PackageLoader("starlette_admin", "templates"),
        ]
    )
)

config.templates = templates

app = Starlette()

```

All templates loaded in the admin site crom from the config that by default
will load from it's own package. The above will include the `templates` directory 
in your own project.

