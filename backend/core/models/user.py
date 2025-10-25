from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, Integer, CheckConstraint
from enum import IntEnum

from .base import Base


class PermissionLevel(IntEnum):
    USER = 1
    MODERATOR = 2
    ADMIN = 3


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
    password: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
    )
    is_superuser: Mapped[bool]
    is_active: Mapped[bool]
    permission_level: Mapped[PermissionLevel] = mapped_column(
        Integer, default=PermissionLevel.USER.value
    )

    __table_args__ = (
        CheckConstraint(
            "permission_level >= 1 AND permission_level <= 3",
            name="check_permission_level_range",
        ),
    )
