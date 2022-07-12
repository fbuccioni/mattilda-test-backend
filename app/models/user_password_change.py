from datetime import datetime
from typing import Optional

from pydantic import Field, BaseModel

from . import abstract


class UserPasswordChange(BaseModel):
    id: Optional[str] = Field(title="ID")
    expires: Optional[datetime] = Field(title="Expiracy")


class UserPasswordChangeInput(abstract.PasswordInputModel):
    pass


class UserPasswordChangeRequest(BaseModel):
    email: str = Field(title="Recover key")

