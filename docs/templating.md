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
from starlette_admin import config as admin_config
from starlette_core.templating import Jinja2Templates

templates = Jinja2Templates(
    loader=jinja2.ChoiceLoader(
        [
            jinja2.FileSystemLoader("templates"),
            jinja2.PackageLoader("starlette_admin", "templates"),
        ]
    )
)

admin_config.templates = templates

app = Starlette()

```

All templates loaded in the admin site crom from the config that by default
will load from it's own package. The above will include the `templates` directory 
in your own project.

## Using `starlette-auth`

This package also includes a set of templates required for when you are using 
the [starlette-auth](https://accent-starlette.github.io/starlette-auth/) 
package which are located [here](https://github.com/accent-starlette/starlette-admin/tree/master/starlette_admin/templates/starlette_admin/auth).

Set the auth config to the templates var from above:

```python
from starlette_auth import config as auth_config

auth_config.templates = templates
```

and set a few env variables to tell `starlette-auth` what the paths are to the templates:

```bash
CHANGE_PW_TEMPLATE="starlette_admin/auth/change_password.html"
LOGIN_TEMPLATE="starlette_admin/auth/login.html"
RESET_PW_TEMPLATE="starlette_admin/auth/reset_password.html"
RESET_PW_DONE_TEMPLATE="starlette_admin/auth/reset_password_done.html"
RESET_PW_CONFIRM_TEMPLATE="starlette_admin/auth/reset_password_confirm.html"
RESET_PW_COMPLETE_TEMPLATE="starlette_admin/auth/reset_password_complete.html"
RESET_PW_EMAIL_SUBJECT_TEMPLATE="starlette_admin/auth/password_reset_subject.txt"
RESET_PW_EMAIL_TEMPLATE="starlette_admin/auth/password_reset_body.txt"
```