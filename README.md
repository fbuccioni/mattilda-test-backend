fastapi-skeretonu
=================


FastAPI Skeleton with the following options


- File structure with models and routes separated
- JWT Auth via `fastapi-jwt-auth` with routes
- `fastapi-pagination`
- Optional SQLModel with migrations via `alembic`
- Optional MongoDB via `fastapi_contrib` package 
  and custom utils 
- Docker support
- Azure functions support
- Util to create a partial model (optional model) for partial
  updates in `app.util.pydantic` package



Create a project with `fastapi-skeretonu`
---------------------------------------

Please rename `project-name` with your project folder name

```
curl -sL https://github.com/fbuccioni/fastapi-skeretonu/tarball/master | tar -zxvf -; mv -v fbuccioni-fastapi-skeretonu-[0-9a-f]*[0-9a-f] project-name
```         
