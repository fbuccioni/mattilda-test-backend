import os
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    app_secret_key: str
    authjwt_secret_key: Optional[str]
    database_default_url: str
    sql_echo: str = 'no'

    class Config:
        env_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '.env')
        )


settings = Settings()
settings.authjwt_secret_key = settings.app_secret_key
