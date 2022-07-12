from pydantic import BaseModel, Field


class MessageOutput(BaseModel):
    detail: str = Field(title="Message")
