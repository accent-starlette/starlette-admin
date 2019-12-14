# Additional Views

To add an additional view to an admin you will need to complete the following:

- Add the new view
- Provide the template loader to the config ([see templating](../templating))
- Add the route name for easy access in the template
- Finally add the new route

```python
from starlette.authentication import has_required_scope
from starlette.exceptions import HTTPException
from starlette_core import config


class PersonAdmin(...):
    @classmethod
    async def some_view(cls, request):
        if not has_required_scope(request, cls.permission_scopes):
            raise HTTPException(403)
        instance = cls.get_object(request)
        context = cls.get_context(request)
        context.update({"object": instance})
        return config.templates.TemplateResponse("some_view.html", context)
    
    @classmethod
    def url_names(cls):
        names = super().url_names()
        mount = cls.mount_name()
        names.update({
            "some_view": f"{cls.site.name}:{mount}_some_view",
        })
        return names

    @classmethod
    def routes(cls):
        router = super().routes()
        mount = cls.mount_name()
        router.add_route(
            "/{id}/some-view",
            endpoint=cls.some_view,
            methods=["GET"],
            name=f"{mount}_some_view",
        )
        return router
```

You will need to show the link to the new view probably the list view or update view.
You can do this by replacing a template. [See templating](../templating). 

You can get the correct url via:

```html
<a href="{{ url_for(url_names.some_view, id=object.id) }}">Some View</a>
```

## Example templates

These can be found in the repo, for example the [update.html](https://github.com/accent-starlette/starlette-admin/blob/master/starlette_admin/templates/starlette_admin/update.html).