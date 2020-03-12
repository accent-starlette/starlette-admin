# Widgets

Widgets can be added to the root page. Widgets are simply a class that has a `context`
and a `render` method.

```python
class BaseWidget:
    template = "starlette_admin/partials/widget.html"

    def get_context(self):
        return {
            "icon": "fa fa-cog",
            "value": 0,
            "text": "Some text",
            "description": "Some useful description",
        }

    def render(self):
        template = config.templates.get_template(self.template)
        return template.render(self.get_context())

    @property
    def html(self):
        return Markup(self.render())
```

The idea here is to inherit from `BaseWidget` and return the required context to
render the template.

In the below example we are using [alpine.js](https://github.com/alpinejs/alpine) 
to change the widgets text to its description when you mouseover the widget.
It also sets a muted class on the `.text` element.

The default template is:

```html
<div class="widget" 
    x-data="{toggle: false, text: '{{ text }}', description: '{{ description }}'}"
    @mouseenter="toggle = true"
    @mouseleave="toggle = false"
>
    <div class="icon"><i class="{{ icon }}"></i></div>
    <div class="content">
        <div class="value">{{ value }}</div>
        <div class="text"
            :class="{'muted': toggle}"
            x-text="toggle ? description : text"
        ></div>
    </div>
</div>
```

## Creating Your Own Widget

The below is a widget that displays the current date.

```python
from datetime import datetime
from starlette_admin.widgets import BaseWidget

class Today(BaseWidget):
    def get_context(self):
        return {
            "icon": "fa fa-calendar",
            "value": datetime.utcnow().strftime("%d %B %Y"),
            "text": "Today",
            "description": "The date as at UTC time"
        }

adminsite = AdminSite(name="admin")

adminsite.register_widget(Today())
```

This will appear on the root page. The free
version of [font awesome](https://fontawesome.com/icons?d=gallery&m=free) is loaded in the template
so you can use any icon class from there.
