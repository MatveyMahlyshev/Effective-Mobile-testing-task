from sqlalchemy.orm import mapped_column, Mapped, SQ
from sqlalchemy import String, SQLEnum
from enum import Enum
from .base import Base

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    last_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    first_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    patronymic: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    password: Mapped[str] = mapped_column(String(60), nullable=False,)
    role = Mapped[str] = mapped_column(SQLEnum(UserRole), nullable=False, default=UserRole.USER,)
    is_active = Mapped[bool]
    