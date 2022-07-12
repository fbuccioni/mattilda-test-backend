from typing import Optional

from sqlmodel import SQLModel, Field

from .. import account_transaction
from ...util import the_ts_now


class AccountTransaction(account_transaction.AccountTransaction, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: int = Field(title="Timestamp", default=the_ts_now)

    __tablename__: str = "accounts_transactions"
