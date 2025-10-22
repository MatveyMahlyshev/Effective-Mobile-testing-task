from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String

from .base import Base


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
