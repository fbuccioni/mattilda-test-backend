from datetime import datetime
from typing import Optional

from pydantic import validator
from sqlmodel import SQLModel, Field, Relationship

from .. import user_password_change
from ... import util
from .user import User


class UserPasswordChange(user_password_change.UserPasswordChange, SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    user: Optional[User] = Relationship(back_populates="password_change_requests")
    burned: bool = Field(title="Is burned", default=False)

    @validator("id", pre=True, always=True)
    def set_id(cls, v, values, **kwargs) -> str:
        if v:
            return v

        return util.password_request_key()

    @validator("expires", pre=True, always=True)
    def set_expires(cls, v, values, **kwargs) -> datetime:
        if v:
            return v

        return util.password_change_request_expiracy()

    __tablename__ = "user_password_change_requests"
