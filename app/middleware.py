from starlette.middleware.cors import CORSMiddleware


class CORSOnAllMiddleware(CORSMiddleware):
    async def __call__(self, scope, receive, send) -> None:
        scope['headers'].append((b'origin', b'allow'))
        return await super().__call__(scope, receive, send)
