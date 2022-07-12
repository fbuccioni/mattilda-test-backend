from fastapi import FastAPI
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi_pagination import add_pagination

from .auth import authjwt_openapi, authjwt_exception_handler
from .middleware import CORSOnAllMiddleware
from .routers import router

# Uncomment below for MongoDB
#from . import mongodb

# Uncomment below for SQL
#from . import sql


app = FastAPI(
    title="FastAPI Skeretonu API",
    version="0.1.0",
    openapi_url="/api/v1/specs/openapi.json",
    docs_url="/api/v1/specs/swagger/",
    redoc_url="/api/v1/specs/redoc/"
)

# Uncomment below for MongoDB
#app.on_event('startup')(mongodb.init)
#mongodb.setup(app)

# Uncomment below for SQL
#app.on_event('startup')(sql.init)


app.exception_handler(AuthJWTException)(authjwt_exception_handler)
origins = ['*']

app.include_router(router)
app.add_middleware(
    CORSOnAllMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

authjwt_openapi(app)
add_pagination(app)
