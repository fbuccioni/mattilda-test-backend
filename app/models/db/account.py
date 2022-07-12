from sqlmodel import SQLModel, Field

from .. import account


class Account(account.Account, SQLModel, table=True):
    number: str = Field(title="Account number", primary_key=True)
    manager_user: int = Field(title="Manager user", default=None, foreign_key="users.id")

    __tablename__: str = "accounts"
