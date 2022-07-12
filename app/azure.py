import azure.functions as func
from azure.functions._http_asgi import AsgiResponse, AsgiRequest

from . import app

app_init = False


async def handle_asgi_request(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    asgi_request = AsgiRequest(req, context)
    scope = asgi_request.to_asgi_http_scope()
    asgi_response = await AsgiResponse.from_app(app, scope, req.get_body())
    return asgi_response.to_func_response()


async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    global app_init

    if not app_init:
        await app.router.startup()
        app_init = True

    return await handle_asgi_request(req, context)
