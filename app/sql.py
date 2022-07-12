from sqlmodel import create_engine, SQLModel
from .conf import settings
from sqlalchemy.ext.asyncio import create_async_engine


engine = create_async_engine(
    settings.database_default_url,
    echo=settings.sql_echo.lower() in ('yes', 'y', 't', 'true'),
    future=True
)


async def init():
    # If you dont want to use migrations
    #async with engine.begin() as conn:
    #    await conn.run_sync(SQLModel.metadata.create_all)
    pass
