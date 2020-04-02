# Form Fields & Widgets

We have created a few form fields and widgets as defined below.

## Fields

There are additional form fields created for you to use.

### JSONField

The json field is a simple field that validates the data and raises a form error
if its not valid json.

```python
from wtforms import fields, form, widget
from starlette_admin.forms import fields as admin_fields
from starlette_admin.forms import widgets as admin_widgets

class MyForm(form.Form):
    field = admin_fields.JSONField(
        default=[]
    )
```

### TagsField

The tags field is a simple fields that allows you to enter multiple tags.
The `form.field.data` will be a python list of strings.

This inherits from `starlette_admin.forms.fields.JSONField`.

```python
from wtforms import fields, form, widget
from starlette_admin.forms import fields as admin_fields
from starlette_admin.forms import widgets as admin_widgets

class MyForm(form.Form):
    field = admin_fields.TagsField(
        default=[]
    )
```

## Widgets

There are additional form field widgets created for you to use.

### CheckboxInput

The checkbox widget just carries some simple styling for a more consistent look.

```python
from wtforms import fields, form, widget
from starlette_admin.forms import fields as admin_fields
from starlette_admin.forms import widgets as admin_widgets

class MyForm(form.Form):
    field = fields.BooleanField(
        widget=admin_widgets.CheckboxInput(),
    )
```

and to use as a list of multiple

```python
from wtforms import fields, form, widget
from starlette_admin.forms import fields as admin_fields
from starlette_admin.forms import widgets as admin_widgets

class MyForm(form.Form):
    field = fields.SelectMultipleField(
        choices=(
            ("One", "One"),
            ("Two", "Two"),
            ("Three", "Three"),
            ("Four", "Four"),
            ("Five", "Five"),
        ),
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=admin_widgets.CheckboxInput(),
    )
```

### FileInput

The file input has been hidden and replaced to look more like a form field.

```python
from wtforms import fields, form, widget
from starlette_admin.forms import fields as admin_fields
from starlette_admin.forms import widgets as admin_widgets

class MyForm(form.Form):
    field = fields.FileField(
        widget=admin_widgets.FileInput()
    )
```

### HorizontalSelect

The horizontal select widget is to be used as a replacement for a multiple
select field. This is for a more user friendly experience.

```python
from wtforms import fields, form, widget
from starlette_admin.forms import fields as admin_fields
from starlette_admin.forms import widgets as admin_widgets

class MyForm(form.Form):
    field = fields.SelectMultipleField(
        choices=(
            ("One", "One"),
            ("Two", "Two"),
            ("Three", "Three"),
            ("Four", "Four"),
            ("Five", "Five"),
        ),
        widget=admin_widgets.HorizontalSelect(),
    )
```

### PasswordInput

The password input widget has an icon added to allow visibility of the password
the user has typed.

```python
from wtforms import fields, form, widget
from starlette_admin.forms import fields as admin_fields
from starlette_admin.forms import widgets as admin_widgets

class MyForm(form.Form):
    field = fields.PasswordField(
        widget=admin_widgets.PasswordInput(),
    )
```

### RadioInput

The radio widget just carries some simple styling for a more consistent look.

```python
from wtforms import fields, form, widget
from starlette_admin.forms import fields as admin_fields
from starlette_admin.forms import widgets as admin_widgets

class MyForm(form.Form):
    field = fields.RadioField(
        choices=(
            ("One", "One"),
            ("Two", "Two"),
            ("Three", "Three"),
            ("Four", "Four"),
            ("Five", "Five"),
        ),
        option_widget=admin_widgets.RadioInput(),
    )
```

### Select

The select widget just carries some simple styling for a more consistent look.

```python
from wtforms import fields, form, widget
from starlette_admin.forms import fields as admin_fields
from starlette_admin.forms import widgets as admin_widgets

class MyForm(form.Form):
    field = fields.SelectField(
        choices=(
            ("", "Please Select.."),
            ("Male", "Male"),
            ("Female", "Female"),
        ),
        widget=admin_widgets.Select(),
    )
```