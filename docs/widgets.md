# Widgets

Widgets can be added to the root page. Widgets are simply a class that has a `context`
and a `render` method.

```python
class BaseWidget:
    template = "starlette_admin/partials/widget.html"

    def get_context(self):
        return {"icon": "fa fa-cog", "value": 0, "text": "Some text"}

    def render(self):
        template = config.templates.get_template(self.template)
        return template.render(self.get_context())

    @property
    def html(self):
        return Markup(self.render())
```

The idea here is to inherit from `BaseWidget` and return the required context to
render the template.

The default template is:

```html
<div class="widget">
    <div class="icon"><i class="{{ icon }}"></i></div>
    <div class="content">
        <div class="value">{{ value }}</div>
        <div class="text">{{ text }}</div>
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
            "value": datetime.now().strftime("%d %B %Y"),
            "text": "Today"
        }

adminsite = AdminSite(name="admin")

adminsite.register_widget(Today())
```

This will appear on the root page. If any widgets are added to the home page the free
version of [font awesome](https://fontawesome.com/icons?d=gallery&m=free) is loaded in the template
so you can use any icon class from there.
