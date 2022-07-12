from typing import Optional

from pydantic import BaseModel, Field

from ..util import the_ts_now


class AccountTransaction(BaseModel):
    id: Optional[int] = Field(title="ID")
    date: int = Field(title="Timestamp")
    account_number: str = Field(title="Account number")
    user: Optional[int] = Field(title="User")
    document: Optional[str] = Field(title="Document associated to transaction")
    description: str = Field(title="Description")
    amount: float = Field(title="Amount", description="Negative if outgoing, positive if incoming")


class TransactionDetail(BaseModel):
    name: str = Field(title="Name")
    country_commercial_id: str = Field(title="Country commercial ID")
    note: str = Field(title="Transaction note")
    amount: float = Field(title="Amount", gt=0)


class AccountBalanceTransaction(AccountTransaction):
    account_amount: float = Field(
        title="Account amount", description="Current amount of the account after transaction"
    )