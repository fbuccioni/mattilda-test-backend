import abc
from typing import Optional, Mapping, Any

from pydantic import BaseModel, Field, validator


class NotSet():
    pass


class PasswordInputModel(BaseModel, abc.ABC):
    password: str = Field(title="Password")
    password_confirm: str = Field(title='Password confirm')

    @staticmethod
    def _validate_password(password: Optional[str], confirm: Optional[str]):
        if (
            not (password is NotSet or confirm is NotSet)
            and password is not None and confirm is not None
            and password != confirm
        ):
            raise ValueError("Passwords don't match")

    @validator("password")
    def validate_password(cls, password: str, values: Mapping[str, Any]):
        cls._validate_password(password, values.get('password_confirm', NotSet))
        return password

    @validator("password_confirm")
    def validate_password_confirm(cls, confirm: str, values: Mapping[str, Any]):
        cls._validate_password(values.get('password', NotSet), confirm)
        return confirm
