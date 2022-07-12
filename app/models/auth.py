from pydantic import BaseModel, Field


class Login(BaseModel):
    username: str = Field(title="User name")
    password: str = Field(title="Password")


class JWTToken(BaseModel):
    access_token: str = Field(title="JWT access token")
    access_token_expires: int = Field(title="JWT access token expires timestamp (milis)")
    refresh_token: str = Field(title="JWT refresh token")
    refresh_token_expires: int = Field(title="JWT refresh token expires timestamp (milis)")
