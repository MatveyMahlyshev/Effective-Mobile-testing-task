from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime
from datetime import datetime

from .base import Base


class Token(Base):
    token: Mapped[str] = mapped_column(String(512))