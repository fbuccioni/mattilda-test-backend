import inspect
import os
import re

from fastapi import Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import ORJSONResponse as JSONResponse
from fastapi.routing import APIRoute
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

from .conf import settings


@AuthJWT.load_config
def get_config():
    return settings


def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


def authjwt_openapi(app):
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

        openapi_schema["components"]["securitySchemes"] = {
            "Bearer Auth": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": "Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token"
            }
        }

        # Get all routes where jwt_optional() or jwt_required
        api_router = [route for route in app.routes if isinstance(route, APIRoute)]

        for route in api_router:
            path = getattr(route, "path")
            endpoint = getattr(route, "endpoint")
            methods = [method.lower() for method in getattr(route, "methods")]

            for method in methods:
                # access_token
                if (
                    re.search(
                        "\.\s*((fresh_)?jwt_)(required|ptional)",
                        inspect.getsource(endpoint),
                        flags=re.DOTALL | re.UNICODE | re.MULTILINE
                    )
                ):
                    openapi_schema["paths"][path][method]["security"] = [{"Bearer Auth": []}]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
