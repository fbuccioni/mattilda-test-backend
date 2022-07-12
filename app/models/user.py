from typing import Optional

from pydantic import BaseModel, Field, EmailStr, constr

from ..util.pydantic import partial_model

PhoneStr = constr(regex="^\+[0-9 \)-]+$")


class User(BaseModel):
    id: Optional[int] = Field(title="ID")

    first_company_name: str = Field(title="First or company name")
    following_names: Optional[str] = Field(title="Following names")
    first_surname: Optional[str] = Field(title="First surname")
    last_surname: Optional[str] = Field(title="Last surname")

    is_company: bool = Field(title="Is company")

    country: str = Field(title="Country", max_length=2)
    country_commercial_id: str = Field(title="Commercial ID")
    country_personal_id: Optional[str] = Field("Personal ID (if person)")

    email: EmailStr = Field(title="Email")
    phone: PhoneStr = Field(title="Phone")
    address: str = Field(title="Address")
    enabled: bool = Field(title="Enabled", default=True)

    role: str = Field(title="Role", default="user")


@partial_model
class PartialUser(User):
    pass
