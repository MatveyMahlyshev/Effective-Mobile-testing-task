from pydantic import BaseModel, EmailStr, ConfigDict, Field

from annotated_types import MaxLen, MinLen

from typing import Annotated

from core.models.user import UserRole

class UserBase(BaseModel):
    email: Annotated[EmailStr, MinLen(5), MaxLen(255)]
    role: UserRole = UserRole.USER
    is_active: bool = False

class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class UserCreate(UserBase):
    last_name: str = Field(min_length=2, max_length=50)
    first_name: str = Field(min_length=2, max_length=50)
    patronymic: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=10, max_length=25)
    confirm_password: str = Field(min_length=10, max_length=25)