from pydantic import BaseModel, ConfigDict, EmailStr, Field
from annotated_types import MinLen, MaxLen
from typing import Annotated


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


class UserAuthSchema(BaseModel):
    model_config = ConfigDict(strict=True)
    email: Annotated[EmailStr, MinLen(5), MaxLen(255)]
    password: str = Field(min_length=10, max_length=25)
