from pydantic import BaseModel, EmailStr, ConfigDict, Field, model_validator
from fastapi import HTTPException, status
from annotated_types import MaxLen, MinLen

from typing import Annotated


class UserEmail(BaseModel):
    email: Annotated[EmailStr, MinLen(5), MaxLen(255)]


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    last_name: str = Field(
        min_length=2,
        max_length=50,
    )
    first_name: str = Field(
        min_length=2,
        max_length=50,
    )
    patronymic: str = Field(
        min_length=2,
        max_length=50,
    )


class UserCreate(UserBase, UserEmail):
    password: str = Field(
        min_length=10,
        max_length=25,
    )
    confirm_password: str = Field(
        min_length=10,
        max_length=25,
    )

    @model_validator(mode="after")
    def check_passwords_match(self) -> "UserCreate":
        if self.password != self.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Пароли должны совпадать.",
            )
        return self


class UserGet(UserBase, UserEmail):
    id: int
    is_superuser: bool
    is_active: bool
    permission_level: int


class UserEdit(UserBase):
    pass
