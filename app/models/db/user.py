from typing import Optional, List

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship

from .. import user


class User(user.User, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    heroes: List["UserPasswordChange"] = Relationship(back_populates="users")

    __tablename__: str = "users"
    __table_args__ = (
        UniqueConstraint("country_commercial_id", name="unq_user_country_commercial_id"),
        UniqueConstraint("country_personal_id", name="unq_user_country_personal_id"),
    )


class UserAccounts(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="users.id")
    account_number: str = Field(default=None, foreign_key="accounts.number")

    __tablename__: str = "user_accounts"
