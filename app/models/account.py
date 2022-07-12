from typing import Optional

from pydantic import BaseModel, Field


class Account(BaseModel):
    number: str = Field(title="Number")
    manager_user: str = Field(title="Manager user")
    name: str = Field(title="Name")
    country: str = Field(title="Country", max_length=2)
    country_personal_id: Optional[str] = Field("Personal ID (if person)")
    country_commercial_id: str = Field(title="Commercial ID")
    is_company: bool = Field(title="Is a company")
    current_amount: float = Field(title="Current amount", default=0.0)
    min_amount: float = Field(title="Minimum amount", default=0.0)
    enabled: bool = Field(title="Enabled")
