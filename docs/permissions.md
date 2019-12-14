# Permissions

Assuming you want to lock down the admin site to only allow authenticated 
users access to it. In starlette there is an `AuthenticationMiddleware` that handles
authentication and permissions.

The below is an example of a dummy user auth backend that simulates a logged-in user.

```python
from starlette.authentication import AuthCredentials, AuthenticationBackend, SimpleUser
from starlette.middleware.authentication import AuthenticationMiddleware

# change our adminsite to require the permission_scopes of "authenticated" and "admin"
adminsite = AdminSite(name="admin", permission_scopes=["authenticated", "admin"])

# define our example auth backend
class DummyAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        # to simulate not logged in, just return out of this function
        return AuthCredentials(["authenticated", "admin"]), SimpleUser("John Smith")

# add the auth middleware
app.add_middleware(AuthenticationMiddleware, backend=DummyAuthBackend())
```

Now when you refresh the site, John Smith's name will appear and only authenticate admin
users will be allowed in.

## Reality Check

In reality you wont be using a dummy auth backend, this is only an example.